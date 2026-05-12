# Bean 字段对照表

本文件记录所有 Bean/Model 中英文字段的对照关系，方便开发时查阅。

---

## 通用字段

| 英文字段 | 中文含义 |
|---|---|
| code / stockCode | 股票代码 |
| name / stockName | 股票名称 |
| date | 日期 |
| provider | 数据提供方 |

---

## DailyBarBean（日K线数据）

| 英文字段 | 中文含义 |
|---|---|
| date | 日期（YYYY-MM-DD） |
| open | 开盘价 |
| high | 最高价 |
| low | 最低价 |
| close | 收盘价 |
| volume | 成交量 |
| code | 股票代码 |
| provider | 数据提供方 |

---

## RealtimeQuoteBean（实时行情数据）

| 英文字段 | 中文含义 |
|---|---|
| code | 股票代码 |
| name | 股票名称 |
| price | 当前价格 |
| change | 涨跌额 |
| change_pct | 涨跌幅（%） |
| volume | 成交量 |
| amount | 成交额 |
| provider | 数据提供方 |

---

## MarketSentimentBean（市场情绪数据）

| 英文字段 | 中文含义 |
|---|---|
| up_count | 上涨股票数量 |
| down_count | 下跌股票数量 |
| up_down_ratio | 涨跌比例（上涨数/下跌数） |
| limit_up_count | 涨停股票数量 |
| limit_down_count | 跌停股票数量 |
| limit_ratio | 涨跌停比例（涨停数/跌停数） |
| blow_rate | 炸板率（%） |
| max_streak | 最高连板数（板） |
| total_volume | 总成交额（元） |
| volume_vs_yesterday | 成交量相较昨日变化（%） |
| avg_change_pct | 平均涨跌幅（%） |
| max_change_pct | 最大涨幅（%） |
| provider | 数据提供方 |

---

## TodayBillBean（日内分钟级单子流入流出数据）

| 英文字段 | 中文含义 |
|---|---|
| time | 时间（HH:MM） |
| main_net_inflow | 主力净流入（元） |
| main_inflow | 主力流入（元） |
| main_outflow | 主力流出（元） |
| main_inflow_pct | 主力净流入占比（%） |
| super_large_net_inflow | 超大单净流入（元） |
| super_large_inflow | 超大单流入（元） |
| super_large_outflow | 超大单流出（元） |
| super_large_inflow_pct | 超大单净流入占比（%） |
| large_net_inflow | 大单净流入（元） |
| large_inflow | 大单流入（元） |
| large_outflow | 大单流出（元） |
| large_inflow_pct | 大单净流入占比（%） |
| medium_net_inflow | 中单净流入（元） |
| medium_inflow | 中单流入（元） |
| medium_outflow | 中单流出（元） |
| medium_inflow_pct | 中单净流入占比（%） |
| small_net_inflow | 小单净流入（元） |
| small_inflow | 小单流入（元） |
| small_outflow | 小单流出（元） |
| small_inflow_pct | 小单净流入占比（%） |
| price | 当前价格 |

---

> 规范：所有新增 Bean/Model 都放在 `app/bean/` 目录下，并在此文件补充字段说明。
