import concurrent
import glob
import os
import json
import logging
import time
from typing import List, Dict
import pandas as pd
import requests
import tiktoken
from retry import retry
# 构造请求头
from fake_useragent import UserAgent
import urllib3

urllib3.disable_warnings()
from format_to_json import parse_openai_arguments_sync
from concurrent.futures import ThreadPoolExecutor
import threading

# 写入文件的锁
file_lock = threading.Lock()
from prompt import PROMPT

# ======== 模型与端点 ========
MODEL = os.getenv("OPENAI_MODEL", "deepseek-ai/DeepSeek-R1")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
CHAT_URL = f"{BASE_URL}/chat/completions"
API_URL_DEFAULT = f"{BASE_URL}/user/info"

# ======== Keys ========
API_KEYS = []
if os.path.exists("自己的keys.txt"):
    with open("自己的keys.txt", "r", encoding="utf-8") as f:
        for line in f:
            k = line.strip()
            if k:
                API_KEYS.append(k)
if not API_KEYS:
    k = os.getenv("OPENAI_API_KEY", "")
    if k:
        API_KEYS = [k]

MIN_BALANCE = float(os.getenv("KEY_MIN_BALANCE", "0"))

# ======== I/O ========
SAVE_DIR = os.getenv("SAVE_DIR", "label_jsons")
RESULT_FILE = os.getenv("RESULT_FILE", f"{SAVE_DIR}/deepseek_results.jsonl")
MD_GLOB = os.getenv("MD_GLOB", r"G:/上市公司年报/TXT/**/*.txt")

# ======== 日志、提示词、分词器 ========
LOG = logging.getLogger("runner")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

enc = tiktoken.get_encoding("o200k_base")


def count_tokens(msgs):
    return sum(len(enc.encode(m["content"])) for m in msgs)


MAX_DOC_TOKENS = int(os.getenv("MAX_DOC_TOKENS", 80000))
PROMPT_HEADROOM = int(os.getenv("PROMPT_HEADROOM", "1024"))
MIN_WINDOW_TOKENS = int(os.getenv("MIN_WINDOW_TOKENS", "1500"))


# ======== 文件读取 ========
def read_text(p: str) -> str:
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        LOG.error(f"[ReadError] {p}: {e}")
        return ""


def truncate_middle_by_tokens(text: str, target_tokens: int) -> str:
    ids = enc.encode(text)
    if len(ids) <= target_tokens:
        return text
    start = max((len(ids) - target_tokens) // 2, 0)
    end = start + target_tokens
    return enc.decode(ids[start:end])


def send_request_once(api_key: str, messages: List[Dict], model: str) -> Dict:
    """
    p: 形如 "ip:port"；在这里拼成 http://user:pass@ip:port
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": UserAgent().random,
    }
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }

    try:
        # 如需使用socks5代理，只需将下面http替换为socks5h即可
        resp = requests.post(CHAT_URL, json=payload, headers=headers, timeout=36000,verify=True)
        # 429：限流，交给上层冷却 + 重试
        if resp.status_code == 429:
            raise RuntimeError("HTTP 429: rate limit")
        elif resp.status_code == 403 and "your account balance is insufficient" in resp.text:
            raise RuntimeError("HTTP 403: insufficient balance" )
        if resp.status_code >= 400:
            # 其它 4xx/5xx：抛异常给上层（tenacity会按策略重试）
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.json()
    except Exception as e:
        print(e)
        # 抛出异常，上层会处理冷却/重试/下线等
        raise


def fetch(query, api_key):
    doc_id = query["doc_id"]
    md_path = query["md_path"]

    content = read_text(md_path)
    if not content:
        LOG.error(f"[{doc_id}] 空文档，跳过")
        return {}

    prompt_tokens = len(enc.encode(PROMPT))
    avail = max(MAX_DOC_TOKENS - prompt_tokens - PROMPT_HEADROOM, MIN_WINDOW_TOKENS)
    if len(enc.encode(content)) > avail:
        LOG.info(f"[{doc_id}] 文档过长，截取 {avail} tokens 中窗")
        content = truncate_middle_by_tokens(content, avail)

    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": content},
    ]
    tokens = count_tokens(messages)

    LOG.info(f"[SEND] {doc_id} tokens={tokens}")
    try:
        # 用线程跑阻塞的 requests
        res_json = send_request_once(api_key, messages, MODEL)
        choices = res_json.get("choices", [])
        if choices:
            msg = choices[0].get("message", {}) or {}
            raw = msg.get("content", "")
        else:
            raw = json.dumps(res_json, ensure_ascii=False)
        # 🔧 加入智能 JSON 解析
        cleaned, data = parse_openai_arguments_sync(raw)
        response_obj = data if isinstance(data, dict) and data else cleaned

        record = {"doc_id": doc_id, "response": response_obj, "md_path": md_path}
        with file_lock:
            os.makedirs(SAVE_DIR, exist_ok=True)
            with open(RESULT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return record

    except Exception as e:
        lower = str(e).lower()
        LOG.error("Request failed for %s: %s", doc_id, type(e).__name__)


# ======== 读取路径 ========
def gather_md_paths() -> List[str]:
    paths = glob.glob(MD_GLOB, recursive=True)
    uniq, seen = [], set()
    for p in paths:
        if p not in seen and os.path.isfile(p):
            uniq.append(p)
            seen.add(p)
    return uniq


# ======== 主流程 ========
def main():
    if not API_KEYS:
        raise RuntimeError("请提供至少一个 API Key：100.txt 或 OPENAI_API_KEY")

    if os.path.exists(RESULT_FILE):
        df = pd.read_json(RESULT_FILE, lines=True, dtype=str)
        processed_ids = set(df["doc_id"].dropna().tolist())
    else:
        processed_ids = set()

    paths = gather_md_paths()
    all_queries = []
    for p in paths:
        if "已取消" in p:
            continue
        # 兼容 .md 和 .txt
        base = os.path.basename(p)
        doc_id = base.replace(".md", "")
        if doc_id in processed_ids:
            continue
        all_queries.append({"doc_id": doc_id, "md_path": p})

    LOG.info(f"Total queries: {len(all_queries)}")
    # 设置五个线程的线程池
    threading_pool = ThreadPoolExecutor(max_workers=5)
    tasks = []

    for i, query in enumerate(all_queries):
        api_key = API_KEYS[i % len(API_KEYS)]
        task = threading_pool.submit(fetch, query, api_key)
        tasks.append(task)
    # 等待所有任务完成
    for task in concurrent.futures.as_completed(tasks):
        result = task.result()
        if result:
            LOG.info(f"完成: {result['doc_id']}")


if __name__ == "__main__":
    os.makedirs(SAVE_DIR, exist_ok=True)
    main()
