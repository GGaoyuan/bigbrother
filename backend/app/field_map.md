# Field Map（字段对照总表）

项目内所有 provider model 字段的中英对照总表。

> 维护规范：每次新增/修改 provider model 字段后，**必须**同步更新本文件。详见 `provider-organization` skill。

| 英文字段 | 中文含义 |
| --- | --- |
| stock_code | 股票代码 |
| stock_name | 股票名称 |
| sw_level | 申万行业级别（1/2/3） |
| sw_industry_code | 申万行业代码（如 "801010.SI"） |
| sw_industry_name | 申万行业名称 |
| sw_parent_industry | 申万上级行业名称 |
| sw_component_count | 申万行业成份个数 |
| sw_weight | 申万最新权重 |
| sw_inclusion_date | 申万计入日期 |
| sw_industry_l1_name | 所属申万一级行业名称 |
| sw_industry_l2_name | 所属申万二级行业名称 |
| sw_industry_l3_name | 所属申万三级行业名称 |
| sw_industry_l1_code | 所属申万一级行业代码 |
| sw_industry_l2_code | 所属申万二级行业代码 |
| sw_industry_l3_code | 所属申万三级行业代码 |
| pe_static | 静态市盈率 |
| pe_ttm | TTM(滚动)市盈率 |
| pe_ratio | 市盈率 |
| pe_ratio_ttm | TTM 市盈率 |
| pb | 市净率 |
| pb_ratio | 市净率 |
| dividend_yield | 股息率（%） |
| price | 当前价格 |
| market_cap | 市值 |
| net_profit_yoy_q3 | 归母净利润同比增长（三季度末，%） |
| net_profit_yoy_q2 | 归母净利润同比增长（二季度末，%） |
| revenue_yoy_q3 | 营业收入同比增长（三季度末，%） |
| revenue_yoy_q2 | 营业收入同比增长（二季度末，%） |
| change_pct | 涨跌幅（%） |
| turnover_rate | 换手率（%） |
| turnover | 成交额（元） |
| fund_inflow | 流入资金（元） |
| fund_outflow | 流出资金（元） |
| fund_net_inflow | 资金净流入（元，流入-流出） |
