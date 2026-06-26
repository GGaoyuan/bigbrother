# mootdx 接口文档

> 基于实际安装版本 **mootdx 0.11.7** 从源码反查整理（官方在线文档已失效）。
> 数据来源：直连通达信行情服务器，**无需安装通达信客户端、无需虚拟机**，Mac / Linux / Windows 原生可用。
>
> 所有行情查询方法返回 `pandas.DataFrame`，无数据时返回 `None` 或空 DataFrame。

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [标准行情 StdQuotes](#标准行情-stdquotes)
- [K 线频率（frequency）枚举](#k-线频率frequency枚举)
- [扩展行情 ExtQuotes（期货 / 期权 / 外盘）](#扩展行情-extquotes期货--期权--外盘)
- [本地数据解析 Reader](#本地数据解析-reader)
- [市场代码约定](#市场代码约定)
- [注意事项](#注意事项)

## 安装

```bash
pip install mootdx
```

> 注意：mootdx 0.11.7 会把 `httpx` 约束到 `0.25.2`。若项目其它部分依赖更高版本 httpx，安装后需自行核对兼容性。

## 快速开始

```python
from mootdx.quotes import Quotes

# 标准市场行情（沪深 A 股、指数等）
client = Quotes.factory(market='std')

# 实时行情
client.quotes(symbol=['000001', '600000'])

# 日线 K 线（最近 60 根）
client.bars(symbol='600000', frequency=9, offset=60)
```

`Quotes.factory(market='std', **kwargs)` 的 `market`：

| 取值 | 含义 |
|------|------|
| `'std'` | 标准行情（沪深 A 股、指数、基金） |
| `'ext'` | 扩展行情（期货、期权、外盘等） |

## 标准行情 StdQuotes

通过 `Quotes.factory(market='std')` 获得。以下方法均为该实例的方法。

### quotes(symbol) — 实时行情快照

```python
client.quotes(symbol=['000001', '600000'])   # 支持单个字符串或代码列表
```

- `symbol`：股票代码，单个字符串或列表。
- 返回字段（部分）：`code` 代码、`price` 现价、`last_close` 昨收、`open/high/low`、`vol` 成交量、`amount` 成交额、`bid1~bid5 / ask1~ask5` 五档买卖价、`bid_vol1~5 / ask_vol1~5` 五档量、`servertime` 服务器时间。
- 涨跌幅需自行计算：`(price - last_close) / last_close * 100`。

### bars(symbol, frequency, start, offset) — K 线

```python
client.bars(symbol='600000', frequency=9, start=0, offset=800)
```

- `symbol`：股票代码。
- `frequency`：K 线频率，见 [频率枚举](#k-线频率frequency枚举)，默认 `9`（日线）。
- `start`：起始位置，默认 `0`（从最新一根往前数）。
- `offset`：返回条数，默认 `800`。
- 返回字段：`open/close/high/low`、`vol` 成交量、`amount` 成交额、`datetime` 时间、`year/month/day/hour/minute`，索引为 `datetime`。

### index(symbol, frequency, start, offset) — 指数 K 线

```python
client.index(symbol='000001', frequency=9, offset=800)
```

- 用于获取指数 K 线，参数同 `bars`。`index_bars` 是它的别名。

### minute(symbol) — 当日实时分时

```python
client.minute(symbol='600000')
```

- 返回当日分时数据（DataFrame）。

### minutes(symbol, date) — 历史分时

```python
client.minutes(symbol='600000', date='20191023')
```

- `date`：查询日期，`YYYYMMDD`。

### transaction(symbol, start, offset) — 当日分笔成交

```python
client.transaction(symbol='600000', start=0, offset=800)
```

### transactions(symbol, start, offset, date) — 历史分笔成交

```python
client.transactions(symbol='600000', date='20170209', start=0, offset=800)
```

### k(symbol, begin, end) — 按日期区间读 K 线

```python
client.k(symbol='600000', begin='2024-01-01', end='2024-12-31')
```

- `begin` / `end`：开始与截止日期。

### F10C(symbol) — 公司信息目录

```python
client.F10C(symbol='600000')
```

- 返回该股票可查询的 F10 信息板块目录（标题列表）。

### F10(symbol, name) — 公司信息详情

```python
client.F10(symbol='600000', name='公司概况')
```

- `name`：F10 标题，取值来自 `F10C` 返回的目录。

### finance(symbol) — 财务信息

```python
client.finance(symbol='000001')
```

### xdxr(symbol) — 除权除息信息

```python
client.xdxr(symbol='600000')
```

- 用于复权计算的除权除息数据。

### stocks(market) — 股票列表

```python
client.stocks(market=1)   # 0 深圳, 1 上海
```

### stock_count(market) — 市场股票数量

```python
client.stock_count(market=1)
```

### block(tofile) — 板块信息

```python
client.block(tofile='block.dat')
```

- 获取证券板块成分信息，可保存到文件。

## K 线频率（frequency）枚举

`bars` / `index` 的 `frequency` 取值（来自源码 `index()` 文档）：

| 值 | 含义 |
|----|------|
| 0 | 5 分钟 K 线 |
| 1 | 15 分钟 K 线 |
| 2 | 30 分钟 K 线 |
| 3 | 1 小时 K 线 |
| 4 | 日 K 线 |
| 5 | 周 K 线 |
| 6 | 月 K 线 |
| 7 | 1 分钟 |
| 8 | 1 分钟 K 线 |
| 9 | 日 K 线 |
| 10 | 季 K 线 |
| 11 | 年 K 线 |

> 日线常用 `9`（也可用 `4`）。分钟线最常用 `8`（1 分钟）、`0`（5 分钟）。

## 扩展行情 ExtQuotes（期货 / 期权 / 外盘）

```python
from mootdx.quotes import Quotes
client = Quotes.factory(market='ext')
```

扩展行情的方法普遍多一个 `market` 参数（市场编号），需配合 `markets()` / `instruments()` 查询。

| 方法 | 说明 |
|------|------|
| `markets()` | 获取实时市场列表 |
| `instrument_count()` | 市场商品数量 |
| `instruments(start, offset)` | 查询所有代码列表 |
| `instrument(start, offset)` | 查询代码列表（分页） |
| `quote(market, symbol)` | 查询五档行情 |
| `minute(market, symbol)` | 查询分时行情 |
| `minutes(market, symbol, date)` | 查询历史分时行情 |
| `bars(frequency, market, symbol, start, offset)` | 查询 K 线数据 |
| `transaction(market, symbol, start, offset)` | 查询分笔成交 |
| `transactions(market, symbol, date, start, offset)` | 查询历史分笔成交 |

```python
client.markets()
client.bars(frequency=9, market=47, symbol='IF2406', offset=100)
```

## 本地数据解析 Reader

解析通达信客户端**本地下载**的数据文件（`.day` / `.lc1` / `.lc5` 等），需要本机已安装通达信并下载过数据，指定 `tdxdir` 数据目录。

```python
from mootdx.reader import Reader
reader = Reader.factory(market='std', tdxdir='C:/new_tdx')

reader.daily(symbol='600000')         # 日线
reader.minute(symbol='600000', suffix=1)  # 分钟线，suffix=1 -> .lc1, 5 -> .lc5
reader.fzline(symbol='600000')        # 5 分钟线
reader.block(symbol='', group=False)  # 板块
reader.block_new(...)                 # 新板块
```

| 方法 | 说明 |
|------|------|
| `daily(symbol)` | 读取本地日线文件 |
| `minute(symbol, suffix)` | 读取本地分钟线，`suffix` 指定 1 分钟/5 分钟 |
| `fzline(symbol)` | 读取本地 5 分钟线 |
| `block(symbol, group)` | 读取板块文件 |
| `block_new(...)` | 读取新版板块文件 |

> Mac 上若没有通达信客户端和本地数据目录，Reader 用不上——直接用 `Quotes`（StdQuotes）联网取数即可。

## 市场代码约定

- 标准行情 `market` 参数：`0` = 深圳，`1` = 上海。
- 股票代码统一用 **6 位数字**字符串：`'600000'`（沪）、`'000001'`（深）。
- mootdx 多数方法可只传代码、自动识别市场。

## 注意事项

1. **资金流不在协议内**：mootdx / pytdx 协议提供的是行情数据（K 线、报价、五档、分笔、分时），**不提供"主力资金流"等衍生指标**——那些由通达信客户端本地公式计算，协议层取不到。板块/个股资金流需用东财、同花顺等数据源。
2. **首次连接较慢**：`factory` 首次会测速选服务器，约数秒；之后较快。可复用同一个 client 实例。
3. **代理干扰**：若系统设置了 HTTP 代理且代理不可用，TCP 直连可能受影响。必要时在进程内设 `NO_PROXY` 绕过。
4. **返回 None / 空表**：代码错误、非交易品种、服务器节点异常都可能返回空，调用方需判空。
5. **频率值有重复语义**：`4` 和 `9` 都是日线，`7` 和 `8` 都涉及 1 分钟，按上表选用即可。

