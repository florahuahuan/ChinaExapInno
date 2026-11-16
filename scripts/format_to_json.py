import json
import re
from typing import Optional

from json_repair import repair_json

FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

def _strip_wrappers(s: str) -> str:
    s = s.strip()
    s = FENCE_RE.sub("", s)
    s = THINK_RE.sub("", s)
    return s.strip()

def _extract_first_json_object(s: str) -> Optional[str]:
    start = s.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return s[start:i+1]
    return None

def parse_openai_arguments_sync(raw_argument_str: str, *, use_repair=True, repair_max_len=120_000):
    original = (raw_argument_str or "").strip()
    if not original:
        return "", {}
    # 快速路径
    try:
        obj = json.loads(original)
        return original, obj
    except Exception:
        pass
    cleaned = _strip_wrappers(original)
    try:
        obj = json.loads(cleaned)
        return cleaned, obj
    except Exception:
        pass
    maybe = _extract_first_json_object(cleaned)
    if maybe:
        try:
            obj = json.loads(maybe)
            return maybe, obj
        except Exception:
            if use_repair:
                snippet = maybe if len(maybe) <= repair_max_len else maybe[:repair_max_len]
                try:
                    repaired = repair_json(snippet)
                    obj = json.loads(repaired)
                    return repaired, obj
                except Exception:
                    return cleaned, {}
            return cleaned, {}
    if use_repair:
        snippet = cleaned if len(cleaned) <= repair_max_len else cleaned[:repair_max_len]
        try:
            repaired = repair_json(snippet)
            obj = json.loads(repaired)
            return repaired, obj
        except Exception:
            return cleaned, {}
    return cleaned, {}

if __name__ == '__main__':
    a = {'id': '0199cac642c18ac1fa7e548c61dc7c0a', 'object': 'chat.completion', 'created': 1760043615, 'model': 'deepseek-ai/DeepSeek-R1', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': '\n{\n  "serendipity_innovation": {\n    "迹象": {\n      "结果": "无",\n      "说明": "年报中未出现任何与意外发现或偶然创新相关的描述。所有研发项目（如中子吸收材料产业化、航空发动机叶片研发）均基于明确的战略规划（\'产业链延伸、价值链延伸\'）和市场需求布局，报告强调\'抓住军民融合、供给侧改革机遇\'的目标导向性，与研发结果一致。"\n    },\n    "识别维度": {\n      "非预期性": {\n        "结果": "否",\n        "说明": "研发目标（核电、航空领域国产化）与实际成果（建成中子吸收材料生产线、签订高温合金叶片合作协议）高度一致。差异仅体现在部分新产品产能未释放导致的利润下滑，但未出现目标外的技术突破。"\n      },\n      "机会识别": {\n        "结果": "否",\n        "说明": "研发过程聚焦于预定的高端装备国产化方向（如响应《中国制造2025》），未提及在研发中意外识别额外适配性。例如，与通用电气的合作是计划内市场拓展，而非意外发现的新应用场景。"\n      },\n      "商业价值转化": {\n        "结果": "否",\n        "说明": "2015年相关创新项目（如核电铸件产业化、航源叶片研发）未产生显著商业价值。年报明示\'新产品未产生收入\'，净利润同比下滑29.44%，主要源于研发投入未能及时转化为收入。"\n      }\n    },\n    "关键词": {\n      "结果": [],\n      "说明": "年报全文未出现任何提供的关键词（如\'偶然\'\'意外\'\'误打误撞\'）。描述创新时采用\'贯彻战略\'\'抓住机遇\'等计划性词汇，无证据表明创新源于非预期事件。"\n    },\n    "技术或功能转移": {\n      "结果": "否",\n      "说明": "虽涉及跨领域（如核电材料延伸至航空），但均为战略驱动的主动拓展（\'价值链延伸\'），非意外功能转移。所有技术应用均限制在原规划场景（如中子吸收材料专用于核电站）。"\n    },\n    "是否偶然发现": {\n      "结果": "否",\n      "说明": "所有案例均为目标导向型研发（如\'产学研合作引进国际先进技术\'）。公司预判核电、航空市场需求后投入资源，并无事先未预料到的技术发现。"\n    },\n    "案例": [\n      {\n        "案例名称": "中子吸收材料产业化",\n        "描述": "全资子公司应流铸造与中国工程物理研究院合作成立应流久源公司，建设国内首条中子吸收材料生产线，应用于核电站后处理。",\n        "说明": "该项目为战略布局（\'产业链延伸\'）结果，非意外发现。依据为年报明确该合作系\'抓住军民融合政策机遇\'，且有中央基建资金支持，不契合serendipity特征。"\n      },\n      {\n        "案例名称": "航空发动机叶片研发",\n        "描述": "应流航源公司与中国航空材料研究院合作，建立高温合金叶片生产线，并与通用电气签订叶片研发协议。",\n        "说明": "属公司\'价值链延伸\'战略的主动行为。年报指出该项目被列为国家专项基金项目并提前规划技术引进，非机缘巧合，故不符合serendipity特征。"\n      }\n    ],\n    "涉及技术": {\n      "结果": ["铸造工艺", "高温合金处理", "精密加工"],\n      "说明": "这些技术支撑了案例实施（如消失模精铸技术用于核主泵叶轮制造、高温合金技术用于航空叶片研发）。"\n    },\n    "技术类型": {\n      "判断结果": "整体性技术",\n      "说明": "依据年报描述的生产模式：1. 功能边界模糊（多种铸造工艺交叉实现定制化功能）；2. 组件依赖性高（产品需整体测试部署）；3. 更新需整体调整（如\'按单定制\'模式，调整需全流程替换）。"\n    },\n    "研发投入背景": {\n      "结果": "持续投入",\n      "说明": "公司长期投入研发（年度研发费用7,047.66万元），通过\'引进领军人才、购置国际设备\'保持技术领先。投入模式促成技术积累，但未触发意外创新。"\n    },\n    "战略一致性": {\n      "结果": "一致",\n      "说明": "创新项目完全契合公司\'产业链延伸、价值链延伸\'战略和《中国制造2025》方向。如航空项目服务于国产化目标，无战略偏离迹象。"\n    },\n    "偏离原因": {\n      "结果": "",\n      "说明": "无偏离，无需填写原因。"\n    },\n    "市场转化": {\n      "是否转化": {\n        "结果": "是",\n        "说明": "部分技术已市场化（中子吸收材料生产线建成），但尚未大规模创收（年报称\'产能未充分释放\'）。"\n      },\n      "应用形式": {\n        "结果": "核电站后处理新材料、航空发动机零部件",\n        "说明": "产业化应用于核电乏燃料处理（如中子吸收材料）和航空装备（如高温合金叶片），场景明确但收益待释放。"\n      }\n    },\n    "可能原因": {\n      "结果": ["政策机会"],\n      "说明": "驱动因素主要为政策机遇（如军民融合、核电国产化政策）。年报未提临时投入或市场偶发需求，强调战略一致性。"\n    }\n  }\n}', 'reasoning_content': '\n首先，我需要仔细阅读查询中的任务：用户要求我作为一名专业的投研分析师，分析安徽应流机电股份有限公司2015年年度报告，特别关注“serendipity_innovation”（意外创新）的多个维度。查询提供了一个JSON输出格式模板，我严格按照这个模板填写结果。模板中包含多个判断标准和技术类型分类。\n\n在报告中，我需要识别是否出现意外创新的迹象。判断迹象的依据来自报告中的具体内容。例如，意外创新通常涉及非预期的发现、机会识别、商业价值转化等维度。用户给出了关键词列表，如“偶然”“意外”“误打误撞”等，我需要基于报告内容检查这些关键词的出现。\n\n接着，技术类型分类是基于用户提供的整体性技术和模块化技术特征。整体性技术的特征包括组件独立性差、接口模糊、更新需要整体替换等；模块化技术则相反。我必须基于报告中描述的技术流程和项目来确定类型。\n\n报告中讨论了多个项目，比如：\n- 与中国工程物理研究院合作成立应流久源公司，从事中子吸收材料产业化。\n- 设立应流航源公司，开发航空发动机零部件。\n- 获得中央基建投资预算950万元用于核电站核一级关键泵阀铸件产业化项目。\n- 与通用电气合作研发高温合金叶片等项目。\n\n这些项目看起来是主动战略投资的成果，旨在延伸产业链和价值链。报告提到“贯彻‘产业链延伸、价值链延伸’战略”，强调“积极开发高端产品”，说明研发是目标导向的。\n\n在关键词方面，我扫描报告全文：未出现“偶然”“意外”“误打误撞”等词汇。描述偏向于计划内行动，如“抓住机遇”“加快实施”等。因此，关键词结果列表为空。\n\n技术转移方面，公司在新领域如核能新材料、航空发动机市场开发，但报告没有提到这些功能是跨场景意外的转移；它们是战略一致性的一部分。\n\n技术类型方面：报告描述公司拥有完整产业链、“五种铸造工艺”，并可以生产多种特殊材质产品。参考技术特征：\n- 组件独立性：报告没明确说明，但基于生产模式（按单定制、整体部署），更接近整体性技术。\n- 接口设计：未提到接口，但定制化生产暗示可能边界模糊。\n- 更新方式：没有具体细节，但高端设备整体替换可能性高。\n- 部署方式：通常整体部署。这些匹配整体性技术特征。\n\n研发投入背景：公司持续投资研发，如“加大技术研发”“引进先进设备”，属于持续投入模式。\n\n战略一致性：所有创新项目都与“产业链延伸、价值链延伸”战略一致，没有偏离。\n\n市场转化：项目如航空发动机叶片已应用或计划应用，但2015年部分产品未产生收入，产能未释放。商业价值表现不足。\n\n驱动因素：可能来自政策机会（核电国产化、中国制造2025），但报告未提“偶然”因素。\n\n最后，案例部分：虽然报告有项目例子，但它们不符合意外特征。如果必须选，我可以列两个，但说明它们为什么不符合serendipity—基于目标和战略规划。\n\n现在，组织JSON输出：\n- “serendipity_innovation”->“迹象”->“结果”：“无”（无意外迹象）\n- 依据：研发目标明确与实际结果一致，创新属于战略规划，无意外发现关键词。\n- 识别维度：非预期性“否”（一致）；机会识别“否”（主动识别）；商业价值转化“否”（未在2015年产生显著价值）。\n- 关键词：空列表，无相关词汇。\n- 技术或功能转移“否”：无跨场景转移描述。\n- 是否偶然发现“否”。\n- 案例：选两个（如中子吸收材料和航空发动机叶片），说明不符合因为计划内。\n- 涉及技术：列相关技术，如铸造、材料处理。\n- 技术类型：判断为“整体性技术”，依据生产模式部署方式。\n- 研发投入背景：“持续投入”。\n- 战略一致性“一致”。\n- 偏离原因：空（因为一致）。\n- 市场转化“已转化”部分，应用形式如产业化生产线。\n- 可能原因：政策机会等。\n'}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 65737, 'completion_tokens': 2034, 'total_tokens': 67771, 'completion_tokens_details': {'reasoning_tokens': 863}}, 'system_fingerprint': ''}
    print(parse_openai_arguments_sync(a['choices'][0]['message']['content'])[-1])
