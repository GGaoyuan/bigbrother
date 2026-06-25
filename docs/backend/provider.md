# Provider 接口目录

`app/providers/` 下所有 provider 文件的接口索引。

---

## index_data.py

返回 model：`IndexDailyBar` / `IndexSpotQuote`
数据源：akshare（东财）
用途：三大指数及风格指数行情

| 方法 | 数据源接口 | 参数 | 返回 |
| --- | --- | --- | --- |
| get_index_daily_hist | ak.index_zh_a_hist | symbol, start_date, end_date | List[IndexDailyBar] |
| get_core_indices_daily | 上证/深成/创业板 | 无 | List[IndexDailyBar] |
| get_style_indices_daily | 沪深300/中证500/1000/2000 | 无 | List[IndexDailyBar] |
| get_index_spot_quotes | ak.stock_zh_index_spot_em | 无 | List[IndexSpotQuote] |

---

## market_breadth.py

返回 model：`MarketSummary` / `LimitPoolStock` / `FundFlowRank`
数据源：akshare
用途：市场宽度、涨跌停池、资金流排名

| 方法 | 数据源接口 | 参数 | 返回 |
| --- | --- | --- | --- |
| get_sse_summary | ak.stock_sse_summary | 无 | List[MarketSummary] |
| get_szse_summary | ak.stock_szse_summary | date | List[MarketSummary] |
| get_market_turnover_snapshot | ak.stock_zh_a_spot_em 聚合 | 无 | dict |
| get_limit_up_pool | ak.stock_zt_pool_em | date | List[LimitPoolStock] |
| get_limit_down_pool | ak.stock_zt_pool_dtgc_em | date | List[LimitPoolStock] |
| get_broken_limit_pool | ak.stock_zt_pool_zbgc_em | date | List[LimitPoolStock] |
| get_strong_pool | ak.stock_zt_pool_strong_em | date | List[LimitPoolStock] |
| get_individual_fund_flow_rank | ak.stock_individual_fund_flow_rank | indicator | List[FundFlowRank] |

---

## board_data.py

返回 model：`BoardQuote` / `SectorFundFlow`
数据源：akshare
用途：东财/同花顺板块行情与资金流

| 方法 | 数据源接口 | 参数 | 返回 |
| --- | --- | --- | --- |
| get_concept_board_quotes | ak.stock_board_concept_name_em | 无 | List[BoardQuote] |
| get_industry_board_quotes | ak.stock_board_industry_name_em | 无 | List[BoardQuote] |
| get_sector_fund_flow_rank | ak.stock_sector_fund_flow_rank | indicator, sector_type | List[SectorFundFlow] |
| get_ths_concept_fund_flow | ak.stock_fund_flow_concept | symbol | List[SectorFundFlow] |
| get_ths_industry_fund_flow | ak.stock_fund_flow_industry | symbol | List[SectorFundFlow] |

---

## capital_data.py

返回 model：`NorthboundFlow` / `MarginBalance` / `DragonTigerEntry` / `MarketFundFlow`
数据源：akshare
用途：北向、两融、龙虎榜、大盘资金流

| 方法 | 数据源接口 | 参数 | 返回 |
| --- | --- | --- | --- |
| get_northbound_summary | ak.stock_hsgt_fund_flow_summary_em | 无 | List[NorthboundFlow] |
| get_northbound_hist | ak.stock_hsgt_hist_em | symbol | List[NorthboundFlow] |
| get_margin_sse | ak.stock_margin_sse | start_date, end_date | List[MarginBalance] |
| get_margin_szse | ak.stock_margin_szse | date | List[MarginBalance] |
| get_dragon_tiger_list | ak.stock_lhb_detail_em | start_date, end_date | List[DragonTigerEntry] |
| get_market_fund_flow | ak.stock_market_fund_flow | 无 | List[MarketFundFlow] |

---

## news_macro.py

返回 model：`NewsItem` / `MacroIndicator` / `OverseasQuote`
数据源：akshare / pywencai（可选）
用途：消息面与海外联动

| 方法 | 数据源接口 | 参数 | 返回 |
| --- | --- | --- | --- |
| get_stock_news | ak.stock_news_em | symbol | List[NewsItem] |
| get_macro_market_operation | ak.macro_china_market_operation | 无 | List[MacroIndicator] |
| get_macro_lpr | ak.macro_china_lpr | 无 | List[MacroIndicator] |
| get_us_index_quotes | ak.index_us_stock_sina | symbol | List[OverseasQuote] |
| get_pywencai_hot_concepts | pywencai.get | query | List[dict] |

---

## individual_net_inflow.py

（保留）同花顺全市场个股资金流

---

## sw_industry_index.py / sw_industry_component.py / sw_industry_third_cons.py

（保留）申万行业体系
