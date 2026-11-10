# 沪深两市每日融资融券汇总

## 数据源选择

遵循根目录 `AGENTS.md`，2026-11-10 核对结果：

1. 当前安装的 mootdx 0.11.7 及其 tdxpy 行情客户端中未找到两市每日两融汇总接口。
2. 检查 easy_tdx 的公开接口文档与 pytdx 的行情客户端源码，未找到对应汇总接口；账户融资融券交易接口不等于市场汇总数据。
3. AKShare 1.20.37 的 `stock_margin_sse` 和 `stock_margin_szse` 已实测返回数据，因此使用这两个现成接口，无需继续寻找其他库或自行写爬虫。

参考来源：

- [easy_tdx 接口](https://github.com/clong365/easy_tdx)
- [pytdx 行情源码](https://github.com/rainx/pytdx/blob/master/pytdx/hq.py)
- [AKShare 沪市实现](https://github.com/akfamily/akshare/blob/main/akshare/stock/flow/stock_margin_sse.py)
- [AKShare 深市实现](https://github.com/akfamily/akshare/blob/main/akshare/stock/flow/stock_margin_szse.py)

## 调用方式

`POST /api/v1/capital/margin`，需要有效 Bearer token。

```json
{"date": "2026-11-09"}
```

请求体可省略或传 `{}`：按上海时区的当前日期，在最近 60 个自然日内寻找两市均已披露数据的最新交易日。指定日期时不自动回退其他日期。此接口一次返回一个日期，不提供历史区间批量查询。

响应使用 `{code, message, data}`。`data` 为最多一条记录的数组；非交易日、数据尚未披露或无共同日期时为 `[]`，数据源错误为 HTTP 502。

每条记录包含 `trade_date`、`units`、`sse`、`szse` 和 `total`。后面三个对象包含：

| 字段 | 含义 |
| --- | --- |
| financing_balance | 融资余额 |
| financing_buy_amount | 融资买入额 |
| financing_repayment_amount | 融资偿还额估算值 |
| securities_lending_balance | 融券余额 |
| securities_sold_volume | 融券卖出量 |
| securities_lending_volume | 融券余量 |
| margin_financing_balance | 融资融券余额 |
| financing_repayment_estimated | 偿还额是否为估算，当前为 true |
| amount_precision | 原始金额的分辨率，单位元 |
| volume_precision | 原始数量的分辨率，单位股/份 |

`sse`、`szse` 额外提供 `source`（SSE/SZSE）和 `library`（akshare）。

## 单位、精度与缺失值

- 沪市 AKShare 返回金额为元，深市为亿元、数量为亿股/亿份；API 将深市乘以 100000000 后合计，使用 Decimal 避免换算误差。
- 深市原始结果只有两位小数，所以换算为元后仍只有百万级分辨率；不会因为换算而获得更高精度。两市合计也受此限制。
- 融资偿还额不在两个库方法返回的汇总字段中，按“前一交易日融资余额 + 当日融资买入额 - 当日融资余额”推算；缺少前序交易日数据时返回 `null`，合计也为 `null`。深市估算同时受源数据舍入影响。
- 始终合计同一交易日的沪深数据。深市日期由 AKShare 的显式 `date` 参数指定；该方法不返回原始日期元数据。
- 缺失或非有限数值报错，不将其补成零。非预期返回结构同样报错，不静默切换数据源。
- 固定版本 AKShare 在原始空结果上会抛出列数不匹配异常，数据层仅识别已验证的“0 列变为 13 列/6 列”空表异常。其他列数变化继续报告错误。升级 AKShare 时需重新检查此行为及返回单位。

## 验证记录

2026-11-10 通过 AKShare 获取 2026-11-09 的两市数据，新接口真实请求返回 HTTP 200；合计融资余额为 2259536259948 元，两融余额为 2288290583750 元。它们是源数据精度下的历史快照，不代表最新值。

离线测试使用真实 AKShare 解析流程，仅替换库的 HTTP 传输，覆盖同日合计、单位、空结果、缺失值、异常、日期窗口和鉴权；另验证 2026-11-08 非交易日的库内空结果行为。
