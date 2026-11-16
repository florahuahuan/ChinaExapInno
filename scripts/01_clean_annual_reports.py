import numpy as np
np.random.seed(1)
import pandas as pd

# 行业股票
industry = pd.read_excel("行业股票.xlsx", dtype=str)
# 代码填充0
industry['股票代码'] = industry['股票代码'].str.zfill(6)
# 读取行业股票数据
industry = industry[['股票代码', '股票板块']]
industry.set_index('股票代码', inplace=True)

df = pd.read_csv("年报.csv", encoding="utf-8-sig")
df['secCode'] = df['secCode'].astype(str)
# 填充0
df['secCode'] = df['secCode'].str.zfill(6)

df = df[["secCode", "secName", "announcementTitle", "announcementTime", "shortTitle", "adjunctUrl"]]
# 将 'announcementTime' 列转换为日期时间格式 '1423497600000' 转换为 '2015-02-10 00:00:00'
df['announcementTime'] = pd.to_datetime(df['announcementTime'], unit='ms')
# 每个股票代码的每一年选择最新时间
df['year'] = df['announcementTime'].dt.year
# 选择每个股票代码的最新公告
df = df.loc[df.groupby(['secCode', 'year'])['announcementTime'].idxmax()]
# 合并数据
df = df.merge(industry, left_on='secCode', right_index=True, how='left')
# 保存
df.to_excel("年报清洗.xlsx", index=False)
# 统计每个股票代码的公告数量
# 'secCode'
grouped = df.groupby('secCode').size().reset_index(name='count')
# 合并数据
grouped = grouped.merge(industry, left_on='secCode', right_index=True, how='left')
grouped.to_excel("统计结果.xlsx", index=False)
# 去掉年报小于10个
grouped = grouped[grouped['count'] >= 10]
# 去重
grouped = grouped.drop_duplicates(subset=['secCode'])
# 每个行业随机选30个股票
industry_fixed = (
    grouped
      .groupby('股票板块')
      .apply(lambda x: x.sample(n=30))
      .reset_index(drop=True)
)
# 保存
industry_fixed.to_excel("随机选取30个股票.xlsx", index=False)
secCodes = industry_fixed['secCode'].tolist()
# 提取年报清洗
df = df[df['secCode'].isin(secCodes)]

# 保存
df.to_excel("最终整理年报.xlsx", index=False)


