import os
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
import re

def do_request_and_save(code, secName, adjunctUrl, year, industry, total, idx):
    # 在 pdfs 下再按行业建子目录
    save_dir = os.path.join("pdfs", industry)
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"{code}_{secName}_{year}.pdf")
    if os.path.exists(save_path):
        print(f"{save_path} 已存在")
        return

    url = "https://static.cninfo.com.cn/"+adjunctUrl
    response = requests.get(url)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)

    print(f"下载完成: {save_path} （{idx+1}/{total}）")

if __name__ == '__main__':
    # 读取时确保带上行业列
    df = pd.read_excel(r"最终整理年报.xlsx", dtype=str)
    total = len(df)

    with ThreadPoolExecutor(max_workers=10) as pool:
        for idx, row in df.iterrows():
            # 提取年份
            announcementTitle = row["announcementTitle"]
            # 提取20xx年
            match = re.search(r"(\d{4})年", announcementTitle)
            if match:
                year = match.group(1)
            else:
                print(f"未找到年份: {announcementTitle}")
                continue
            # year = row["year"]
            code       = row["secCode"].zfill(6)
            secName    = row["secName"].replace("/", "_").replace("*", "")
            adjunctUrl = row["adjunctUrl"]
            industry   = row["股票板块"].replace("/", "_")  # 防止文件夹名里有非法字符
            # do_request_and_save(
            #     code, secName, adjunctUrl,
            #     year, industry,
            #     total, idx
            # )
            pool.submit(
                do_request_and_save,
                code, secName, adjunctUrl,
                year, industry,
                total, idx
            )


