---
name: stock-field-mapping
description: 股票专业名词中英文字段对照表。当编写或修改 FastAPI 项目（FastAPI/）中 provider 调用、model 构造、DataFrame 列名处理代码时使用。Provider（efinance/akshare 等）返回的 DataFrame 列名通常为中文，model 字段名统一为英文，本 skill 提供权威对照表。Examples："股票代码用什么英文名"、"把 efinance 返回值映射成 model"、"这个中文字段对应的 model 字段是什么"。
---

# Stock Field Mapping (股票字段中英文对照)

权威对照表：Provider（efinance / akshare / qstock 等）返回的 DataFrame 中文列名 → FastAPI model 中的英文字段名。

## 使用场景

1. **写 model**：新增 `BaseModel` 时按本表选英文字段名，不要自创命名。
2. **写 provider**：把 DataFrame 中文列重命名为英文时，按本表对应。
3. **写 service**：从 provider 构造 model 时，了解列名已被映射。
4. **新增字段**：provider 返回了表中没有的中文字段，按命名约定补充英文，并把新条目加到本表。

## 命名约定

- 全部 `lower_snake_case`
- 英文语义清晰，避免缩写（除非是金融术语标准缩写：pe、pb、eps、bps、roe）
- 比例/百分比统一加 `_pct` 后缀
- 净流入相关统一 `_inflow` 结尾

## 中英对照表

### 基础信息

| 中文 | 英文 |
| --- | --- |
| 股票代码 | stock_code |
| 股票名称 | stock_name |
| 代码 | code |
| 名称 | name |

### 行情数据

| 中文 | 英文 |
| --- | --- |
| 最新价 | price |
| 今开 / 开盘 / 开盘价 | open |
| 最高 / 最高价 | high |
| 最低 / 最低价 | low |
| 昨收 | prev_close |
| 收盘 / 收盘价 | close |

### 涨跌

| 中文 | 英文 |
| --- | --- |
| 涨跌额 | change |
| 涨跌幅 / 涨幅 | change_pct |

### 成交

| 中文 | 英文 |
| --- | --- |
| 成交量 | volume |
| 成交额 | turnover |
| 换手率 | turnover_rate |
| 量比 | volume_ratio |
| 振幅 | amplitude |
| 外盘 | outer_volume |
| 内盘 | inner_volume |
| 委比 | bid_ask_ratio |

### 资金流向

| 中文 | 英文 |
| --- | --- |
| 主力净流入 | main_net_inflow |
| 主力净流入占比 | main_net_inflow_pct |
| 超大单净流入 | extra_large_order_inflow |
| 超大单净流入占比 | extra_large_order_inflow_pct |
| 大单净流入 | large_order_inflow |
| 大单净流入占比 | large_order_inflow_pct |
| 中单净流入 | medium_order_inflow |
| 中单净流入占比 | medium_order_inflow_pct |
| 小单净流入 | small_order_inflow |
| 小单净流入占比 | small_order_inflow_pct |

### 时间

| 中文 | 英文 |
| --- | --- |
| 日期 | date |
| 时间 | time |

### 市值与股本

| 中文 | 英文 |
| --- | --- |
| 总市值 | total_market_cap |
| 流通市值 | circulating_market_cap |
| 总股本 | total_shares |
| 流通股本 | circulating_shares |

### 估值指标

| 中文 | 英文 |
| --- | --- |
| 市盈率 | pe_ratio |
| 市盈率(动态) | pe_ratio_ttm |
| 市净率 | pb_ratio |
| 每股收益 | eps |
| 每股净资产 | bps |

### 板块行业

| 中文 | 英文 |
| --- | --- |
| 所属行业 | industry |
| 所属板块 | sector |
| 板块名称 | sector_name |
| 板块代码 | sector_code |

### 财务指标

| 中文 | 英文 |
| --- | --- |
| 净利润 | net_profit |
| 毛利率 | gross_margin |
| 净利率 | net_margin |
| 资产负债率 | debt_ratio |
| 速动比率 | quick_ratio |
| ROE | roe |

## 在 provider 中重命名 DataFrame 列名的写法

不再依赖单独的工具模块，直接在 provider 里内联 dict（按本 skill 抄过去）：

```python
df = df.rename(columns={
    "股票代码": "stock_code",
    "时间": "time",
    "主力净流入": "main_net_inflow",
    "小单净流入": "small_order_inflow",
    "中单净流入": "medium_order_inflow",
    "大单净流入": "large_order_inflow",
    "超大单净流入": "extra_large_order_inflow",
})
```

只列出该 provider 实际返回、且 model 实际使用的字段，不要把整张表都搬过来。

## 维护

发现 provider 返回了表中没有的中文字段：

1. 按命名约定起一个英文名
2. 把新条目加到本文件对应分类下
3. 同步更新调用处的 `rename` 字典
