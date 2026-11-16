import json
import os
import requests
import pandas as pd

headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.cninfo.com.cn",
    "Pragma": "no-cache",
    "Proxy-Connection": "keep-alive",
    "Referer": "https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
cookies = {

}


def get_list(stock, seDate):
    url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
    data = {
        "pageNum": "1",
        "pageSize": "30",
        "column": "szse",
        "tabName": "fulltext",
        "plate": "",
        "stock": stock,
        "searchkey": "",
        "secid": "",
        "category": "category_ndbg_szsh",
        "trade": "",
        "seDate": seDate,
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true"
    }
    response = requests.post(url, headers=headers, cookies=cookies, data=data, verify=True)

    totalpages = response.json()["totalpages"]
    announcements = response.json()["announcements"]
    return totalpages, announcements


def save_csv(res):
    df = pd.DataFrame(res)
    if not os.path.exists("年报.csv"):
        df.to_csv("年报.csv", index=False, encoding="utf-8-sig")
    else:
        df.to_csv("年报.csv", mode="a", header=False, index=False, encoding="utf-8-sig")

if __name__ == '__main__':
    with open("szse_stock.json", "r", encoding="utf-8") as f:
        szse_lis = json.load(f)["stockList"]
    # 读取爬过的
    if os.path.exists("年报.csv"):
        df = pd.read_csv("年报.csv", dtype=str)
        ids = df["secCode"].tolist()
    else:
        df = pd.DataFrame()
        ids = []
    df_input = pd.read_excel("行业股票.xlsx",dtype=str)
    # 去重股票
    df_input.drop_duplicates(subset=["股票代码"], inplace=True)
    for index, row in df_input.iterrows():
        # 股票代码	股票名称	股票板块
        stock_code = row['股票代码']
        # 填充0
        stock_code = stock_code.zfill(6)
        if stock_code in ids:
            print(f"已存在股票代码: {stock_code}")
            continue
        for szse in szse_lis:
            if szse["code"] == stock_code:
                orgId = szse["orgId"]
                break
        else:
            print(f"未找到股票代码: {stock_code}")
            continue
        stock = f"{stock_code},{orgId}"
        for year in range(2001, 2025):
            seDate = f"{year}-01-01~{year}-12-31"
            totalpages, announcements = get_list(stock, seDate)
            save_csv(announcements)
