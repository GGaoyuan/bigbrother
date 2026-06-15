# A股市场分析 - 数据需求与接口清单

> 用途：对上证指数、深证成指、创业板指做全面市场分析（趋势、资金、板块、消息面）
> 主要数据源：AKShare（首选，覆盖最全）、efinance（备选，东财数据较快）、pywencai（同花顺问财，热点题材好用）
>
> 安装：
> ```bash
> pip install akshare efinance pywencai pandas
> ```

---

## 一、指数行情数据（趋势/支撑压力/均线）

**目标：** 判断牛/熊/震荡市，识别支撑压力位，观察均线排列

| 数据项 | 库 | 接口 | 关键参数 |
|--------|----|----|---------|
| 三大指数日K历史数据 | akshare | `ak.stock_zh_index_daily_em(symbol)` | symbol="sh000001"(上证)/"sz399001"(深成)/"sz399006"(创业板) |
| 三大指数日K（备选） | akshare | `ak.index_zh_a_hist(symbol, period, start_date, end_date)` | symbol="000001"/"399001"/"399006"，period="daily" |
| 实时指数行情 | akshare | `ak.stock_zh_index_spot_em(symbol="指数成份")` | 沪深重要指数实时快照 |
| 指数分钟K线 | akshare | `ak.index_zh_a_hist_min_em(symbol, period)` | period="1"/"5"/"15"/"30"/"60" |
| 指数行情（备选） | efinance | `ef.stock.get_quote_history("000001", klt=101)` | klt: 101日/102周/103月/5/15/30/60分钟 |

**衍生计算（pandas 自己算）：**
- MA5 / MA10 / MA20 / MA60 / MA120 / MA250
- 支撑位/压力位：近 60/120 日的局部高低点（极值检测）
- MACD / KDJ / RSI（也可用 `talib` 库）

---

## 二、成交量与市场宽度

**目标：** 量价配合分析，判断量能趋势

| 数据项 | 库 | 接口 | 备注 |
|--------|----|----|------|
| 两市每日成交额 | akshare | `ak.stock_zh_a_spot_em()` 后聚合 | 全市场实时快照，sum(成交额) |
| 沪市成交统计 | akshare | `ak.stock_sse_summary()` | 上交所市场总貌 |
| 深市成交统计 | akshare | `ak.stock_szse_summary(date)` | 深交所市场总貌 |
| 涨跌停统计 | akshare | `ak.stock_zt_pool_em(date)` | 涨停池（含连板数、封单等） |
| 跌停池 | akshare | `ak.stock_zt_pool_dtgc_em(date)` | 跌停股 |
| 炸板统计 | akshare | `ak.stock_zt_pool_zbgc_em(date)` | 炸板股（涨停后回落） |
| 强势股池 | akshare | `ak.stock_zt_pool_strong_em(date)` | 涨停梯队首板/连板分布 |
| 个股资金流（全市场） | akshare | `ak.stock_individual_fund_flow_rank(indicator)` | indicator="今日"/"3日"/"5日"/"10日" |

---

## 三、板块/题材数据（主线、轮动、热点持续性）

**目标：** 识别当前主线题材、板块轮动、判断大小盘风格

### 3.1 概念板块

| 数据项 | 库 | 接口 | 备注 |
|--------|----|----|------|
| 概念板块实时行情 | akshare | `ak.stock_board_concept_name_em()` | 全部概念板块涨跌幅 |
| 概念板块资金流向 | akshare | `ak.stock_sector_fund_flow_rank(indicator, sector_type)` | sector_type="概念资金流" |
| 概念板块历史K线 | akshare | `ak.stock_board_concept_hist_em(symbol, start_date, end_date)` | symbol=板块名称 |
| 概念板块成份股 | akshare | `ak.stock_board_concept_cons_em(symbol)` | 板块内个股列表 |
| 同花顺概念板块 | akshare | `ak.stock_board_concept_name_ths()` | 同花顺口径 |
| 同花顺概念资金流 | akshare | `ak.stock_fund_flow_concept(symbol="即时")` | 即时/3日/5日/10日 |
| 问财热点（同花顺） | pywencai | `pywencai.get(query="今日涨停概念排行")` | 自然语言查询，热点最准 |

### 3.2 行业板块

| 数据项 | 库 | 接口 | 备注 |
|--------|----|----|------|
| 行业板块实时行情 | akshare | `ak.stock_board_industry_name_em()` | 申万/东财行业 |
| 行业板块资金流向 | akshare | `ak.stock_sector_fund_flow_rank(sector_type="行业资金流")` | 行业主力净流入 |
| 行业板块历史K线 | akshare | `ak.stock_board_industry_hist_em(symbol)` | 板块走势 |
| 同花顺行业资金流 | akshare | `ak.stock_fund_flow_industry(symbol="即时")` | 同花顺口径 |

### 3.3 大小盘风格

| 数据项 | 库 | 接口 | 用途 |
|--------|----|----|------|
| 沪深300历史 | akshare | `ak.index_zh_a_hist(symbol="000300")` | 大票代表 |
| 中证500历史 | akshare | `ak.index_zh_a_hist(symbol="000905")` | 中盘 |
| 中证1000历史 | akshare | `ak.index_zh_a_hist(symbol="000852")` | 小盘 |
| 中证2000历史 | akshare | `ak.index_zh_a_hist(symbol="932000")` | 微盘 |
| 万得微盘股指数 | akshare | `ak.index_hist_sw(symbol="801853")` | 微盘股替代 |

> 大票/小票判断：对比沪深300与中证1000/2000的相对强弱（涨幅差/比值曲线）

---

## 四、资金结构数据

**目标：** 北向、两融、主力、龙虎榜、游资席位

### 4.1 北向资金（沪深股通）

| 数据项 | 库 | 接口 | 备注 |
|--------|----|----|------|
| 北向资金实时净流入 | akshare | `ak.stock_hsgt_fund_flow_summary_em()` | 当日实时 |
| 北向资金历史净流入 | akshare | `ak.stock_hsgt_hist_em(symbol)` | symbol="北向资金"/"沪股通"/"深股通" |
| 北向持股明细 | akshare | `ak.stock_hsgt_hold_stock_em(market, indicator)` | market="北向", indicator="今日"/"3日"/"5日" |
| 北向十大成交活跃股 | akshare | `ak.stock_hsgt_stock_statistics_em(symbol)` | 沪股通/深股通十大活跃 |
| 北向板块排行 | akshare | `ak.stock_hsgt_board_rank_em(symbol, indicator)` | 行业/概念维度 |

### 4.2 两融数据

| 数据项 | 库 | 接口 | 备注 |
|--------|----|----|------|
| 两融余额（沪市） | akshare | `ak.stock_margin_sse(start_date, end_date)` | 上交所每日余额 |
| 两融余额（深市） | akshare | `ak.stock_margin_szse(date)` | 深交所每日余额 |
| 两融明细（个股） | akshare | `ak.stock_margin_detail_szse(date)` | 深市个股明细 |
| 两融总量（汇总） | akshare | `ak.stock_margin_underlying_info_szse(date)` | 标的及汇总 |

### 4.3 龙虎榜

| 数据项 | 库 | 接口 | 备注 |
|--------|----|----|------|
| 当日龙虎榜 | akshare | `ak.stock_lhb_detail_em(start_date, end_date)` | 上榜股票 + 净买/卖 |
| 龙虎榜营业部排行 | akshare | `ak.stock_lhb_yybph_em(symbol)` | symbol="近一月"/"近三月"等 |
| 龙虎榜机构席位 | akshare | `ak.stock_lhb_jgmx_em()` | 机构买卖明细 |
| 营业部追踪（游资） | akshare | `ak.stock_lhb_yyb_detail_em(symbol)` | 知名游资席位历史战绩 |
| 个股龙虎榜历史 | akshare | `ak.stock_lhb_stock_detail_em(symbol)` | 单股上榜记录 |
| 龙虎榜（同花顺） | akshare | `ak.stock_lhb_detail_daily_sina(date)` | 新浪/同花顺口径 |

### 4.4 主力/大单资金

| 数据项 | 库 | 接口 | 备注 |
|--------|----|----|------|
| 个股资金流向 | akshare | `ak.stock_individual_fund_flow(stock, market)` | 单股 5 日明细 |
| 全市场资金流排名 | akshare | `ak.stock_individual_fund_flow_rank(indicator)` | indicator="今日"/"3日"/"5日"/"10日" |
| 主力净流入（板块） | akshare | `ak.stock_sector_fund_flow_rank()` | 板块维度 |
| 大盘资金流向 | akshare | `ak.stock_market_fund_flow()` | 全市场超大单/大单/中单/小单 |

---

## 五、消息与事件面

**目标：** 政策、央行操作、海外联动、重大事件

| 数据项 | 库 | 接口 | 备注 |
|--------|----|----|------|
| 财经新闻（东财） | akshare | `ak.stock_news_em(symbol)` | 个股或大盘新闻 |
| 全球财经快讯 | akshare | `ak.news_economic_baidu(date)` | 百度财经日历 |
| 央行公开市场操作 | akshare | `ak.macro_china_market_operation()` | 逆回购/MLF |
| LPR利率 | akshare | `ak.macro_china_lpr()` | 1Y/5Y LPR |
| 中国宏观日历 | akshare | `ak.news_economic_baidu()` | 重要数据发布预告 |
| 美元指数 | akshare | `ak.fx_quote_baidu(symbol="美元指数")` | 海外联动 |
| 美元/人民币汇率 | akshare | `ak.currency_boc_sina(symbol="USDCNH", indicator)` | 离岸人民币 |
| 美股三大指数 | akshare | `ak.index_us_stock_sina(symbol)` | symbol=".DJI"/".IXIC"/".INX" |
| 港股恒生指数 | akshare | `ak.stock_hk_index_daily_em(symbol="HSI")` | 港股联动 |
| 问财热点新闻 | pywencai | `pywencai.get(query="今日重要消息")` | 自然语言聚合 |

---

## 六、数据获取脚本骨架（建议）

```python
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

today = datetime.now().strftime("%Y%m%d")
start = (datetime.now() - timedelta(days=180)).strftime("%Y%m%d")

# 1. 三大指数
sh = ak.index_zh_a_hist(symbol="000001", period="daily", start_date=start, end_date=today)
sz = ak.index_zh_a_hist(symbol="399001", period="daily", start_date=start, end_date=today)
cyb = ak.index_zh_a_hist(symbol="399006", period="daily", start_date=start, end_date=today)

# 2. 北向资金
north = ak.stock_hsgt_hist_em(symbol="北向资金")

# 3. 龙虎榜
lhb = ak.stock_lhb_detail_em(start_date=today, end_date=today)

# 4. 涨停池
zt = ak.stock_zt_pool_em(date=today)

# 5. 概念板块资金流
concept_flow = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="概念资金流")

# 6. 行业板块资金流
industry_flow = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")

# 7. 大盘资金流
market_flow = ak.stock_market_fund_flow()

# 8. 两融余额
margin_sse = ak.stock_margin_sse(start_date=start, end_date=today)
```

---

## 七、最终分析框架对应表

| 分析维度 | 主要数据 | 主要接口 |
|---------|---------|---------|
| 三大指数趋势 | K线 + 均线 | `index_zh_a_hist` |
| 支撑/压力位 | 历史K线极值 | `index_zh_a_hist` + pandas |
| 牛/熊/震荡判断 | 均线排列 + 趋势线 | `index_zh_a_hist` + 计算 |
| 成交量趋势 | 两市成交额 | `stock_sse_summary` / `stock_szse_summary` |
| 主线题材识别 | 概念涨幅 + 资金流 | `stock_board_concept_name_em` |
| 板块资金流向 | 行业/概念资金净流入 | `stock_sector_fund_flow_rank` |
| 大票 vs 小票 | 沪深300 vs 中证2000 | `index_zh_a_hist` (多指数对比) |
| 板块轮动 | 概念近期涨幅排序变化 | `stock_board_concept_hist_em` |
| 热点持续性 | 涨停梯队 + 连板情况 | `stock_zt_pool_em` |
| 北向资金 | 当日 + 历史净流入 | `stock_hsgt_fund_flow_summary_em` |
| 两融余额 | 沪深两市余额 | `stock_margin_sse` / `stock_margin_szse` |
| 龙虎榜 | 上榜个股 + 席位 | `stock_lhb_detail_em` |
| 游资席位动向 | 营业部追踪 | `stock_lhb_yyb_detail_em` |
| 增量/存量博弈 | 两融变化 + 北向 + 成交量 | 综合 |
| 消息事件 | 财经新闻 + 央行操作 | `stock_news_em` + `macro_china_*` |
| 海外联动 | 美元指数 + 美股 + 港股 | `fx_quote_baidu` + `index_us_stock_sina` |

---

## 八、注意事项

1. **频率限制**：AKShare 部分接口数据来自新浪/东财，频繁调用会被限流。建议加 `time.sleep(0.5~1)`。
2. **数据延迟**：实时接口通常延迟 3-15 秒，盘中分析够用。
3. **盘前/盘后差异**：龙虎榜、涨停池等数据通常在 18:00 后更新当日完整数据。
4. **接口变动**：AKShare 更新频繁，遇到接口失效用 `ak.__version__` 检查版本，必要时 `pip install akshare -U`。
5. **同花顺/东财口径差异**：行业、概念分类不同，建议两边都拉一份对比。
6. **历史数据回填**：第一次分析建议拉 250 个交易日（覆盖年线），之后每日增量更新即可。
