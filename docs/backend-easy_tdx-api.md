# Easy TDX API 文档

## 概述

easy_tdx 是一个通达信 TCP 协议 A 股行情数据客户端，提供同步和异步两种方式访问通达信服务器获取行情数据。

**版本**: 1.14.5  
**数据源**: 通达信 TDX 协议服务器  
**优点**: 
- 免费、稳定
- 支持日内分时数据
- 支持指数数据
- 连接速度快，延迟低

## 安装

```bash
pip install easy_tdx~=1.14.5
```

## 快速开始

### 同步方式

```python
from easy_tdx import TdxClient, Market, KlineCategory

# 使用上下文管理器自动连接和断开
with TdxClient() as client:
    # 获取上证指数日K线
    df = client.get_index_bars(Market.SH, "000001", KlineCategory.DAY, 0, 100)
    print(df)
```

### 异步方式

```python
import asyncio
from easy_tdx import AsyncTdxClient, Market, KlineCategory

async def main():
    async with AsyncTdxClient() as client:
        df = await client.get_index_bars(Market.SH, "000001", KlineCategory.DAY, 0, 100)
        print(df)

asyncio.run(main())
```

## 核心枚举

### Market（市场）

| 枚举值 | 说明 |
|--------|------|
| `Market.SZ` (0) | 深圳市场 |
| `Market.SH` (1) | 上海市场 |
| `Market.BJ` (2) | 北京市场 |

### KlineCategory（K线周期）

| 枚举值 | 说明 |
|--------|------|
| `KlineCategory.MIN_1` (7) | 1分钟线 |
| `KlineCategory.MIN_3` (8) | 3分钟线 |
| `KlineCategory.MIN_5` (0) | 5分钟线 |
| `KlineCategory.MIN_15` (1) | 15分钟线 |
| `KlineCategory.MIN_30` (2) | 30分钟线 |
| `KlineCategory.MIN_60` (3) | 60分钟线 |
| `KlineCategory.DAY` (4) | 日线 |
| `KlineCategory.WEEK` (5) | 周线 |
| `KlineCategory.MONTH` (6) | 月线 |
| `KlineCategory.SEASON` (10) | 季线 |
| `KlineCategory.YEAR` (9) | 年线 |

## 核心 API

### 1. 获取指数K线数据

**方法**: `get_index_bars(market, code, category, start, count=800)`

**参数**:
- `market`: Market 枚举，市场代码
- `code`: str，指数代码（如 "000001" 表示上证指数）
- `category`: KlineCategory 枚举，K线周期
- `start`: int，起始位置（0表示最新）
- `count`: int，数量（最多800条/次）

**返回**: pandas.DataFrame

**字段**:
- `datetime`: 时间戳
- `open`: 开盘价
- `close`: 收盘价
- `high`: 最高价
- `low`: 最低价
- `vol`: 成交量
- `amount`: 成交额

**示例**:
```python
# 获取上证指数最近100根日K线
df = client.get_index_bars(Market.SH, "000001", KlineCategory.DAY, 0, 100)

# 获取深证成指最近200根周K线
df = client.get_index_bars(Market.SZ, "399001", KlineCategory.WEEK, 0, 200)

# 获取创业板指最近500根1分钟K线
df = client.get_index_bars(Market.SZ, "399006", KlineCategory.MIN_1, 0, 500)
```

### 2. 获取股票K线数据

**方法**: `get_security_bars(market, code, category, start, count=800)`

**参数**: 同 `get_index_bars`

**返回**: pandas.DataFrame（字段同上）

**示例**:
```python
# 获取平安银行日K线
df = client.get_security_bars(Market.SZ, "000001", KlineCategory.DAY, 0, 100)

# 获取贵州茅台5分钟K线
df = client.get_security_bars(Market.SH, "600519", KlineCategory.MIN_5, 0, 500)
```

### 3. 获取分时数据

**方法**: `get_minute_time_data(market, code)`

**参数**:
- `market`: Market 枚举
- `code`: str，股票/指数代码

**返回**: pandas.DataFrame（240条当日分时数据）

**字段**:
- `datetime`: 时间戳
- `price`: 价格
- `vol`: 成交量
- `amount`: 成交额
- `average_price`: 均价

**示例**:
```python
# 获取上证指数当日分时
df = client.get_minute_time_data(Market.SH, "000001")
```

### 4. 获取历史分时数据

**方法**: `get_history_minute_time_data(market, code, date)`

**参数**:
- `market`: Market 枚举
- `code`: str，股票/指数代码
- `date`: int，日期（格式：YYYYMMDD，如 20260626）

**返回**: pandas.DataFrame

**示例**:
```python
# 获取2026年6月26日的上证指数分时数据
df = client.get_history_minute_time_data(Market.SH, "000001", 20260626)
```

### 5. 获取股票列表

**方法**: `get_security_list_all(pages="all")`

**参数**:
- `pages`: int | str，页数或 "all" 获取全部

**返回**: pandas.DataFrame

**字段**:
- `code`: 股票代码
- `market`: 市场
- `name`: 股票名称
- `volunit`: 成交量单位
- `decimal_point`: 小数点位数
- `pre_close`: 前收价

**示例**:
```python
# 获取所有股票列表（带缓存，24小时更新一次）
df = client.get_security_list_all()
```

### 6. 获取实时行情

**方法**: `get_security_quotes(stocks)`

**参数**:
- `stocks`: list[tuple[Market, str]]，股票列表

**返回**: pandas.DataFrame

**示例**:
```python
stocks = [
    (Market.SH, "000001"),  # 上证指数
    (Market.SZ, "399001"),  # 深证成指
    (Market.SH, "600519"),  # 贵州茅台
]
df = client.get_security_quotes(stocks)
```

### 7. 获取逐笔成交

**方法**: `get_history_transaction_data(market, code, date, start, count=800)`

**参数**:
- `market`: Market 枚举
- `code`: str，股票代码
- `date`: int，日期（YYYYMMDD）
- `start`: int，起始位置
- `count`: int，数量（最多800条/次）

**返回**: pandas.DataFrame

**字段**:
- `datetime`: 时间戳
- `price`: 成交价
- `vol`: 成交量
- `buyorsell`: 买卖方向（0=买入，1=卖出，2=未知）

**示例**:
```python
# 获取某日的逐笔成交数据
df = client.get_history_transaction_data(Market.SH, "600519", 20260626, 0, 800)
```

## 连接管理

### 自动选择最快服务器

```python
# 不指定服务器，自动从已知列表中选择延迟最低的
with TdxClient() as client:
    df = client.get_index_bars(Market.SH, "000001", KlineCategory.DAY, 0, 100)
```

### 指定服务器

```python
# 指定具体IP
with TdxClient("180.153.18.170") as client:
    df = client.get_index_bars(Market.SH, "000001", KlineCategory.DAY, 0, 100)
```

### 手动测速并保存

```python
from easy_tdx import ping_all, save_best_host

# 测试所有已知服务器
results = ping_all()
print(results)

# 保存延迟最低的服务器
save_best_host()
```

## 异常处理

```python
from easy_tdx import TdxClient, TdxConnectionError, TdxError

try:
    with TdxClient() as client:
        df = client.get_index_bars(Market.SH, "000001", KlineCategory.DAY, 0, 100)
except TdxConnectionError as e:
    print(f"连接错误: {e}")
except TdxError as e:
    print(f"TDX错误: {e}")
```

## 性能优化建议

### 1. 使用上下文管理器

推荐使用 `with` 语句，自动管理连接生命周期：

```python
with TdxClient() as client:
    # 多次调用共享同一连接
    df1 = client.get_index_bars(Market.SH, "000001", KlineCategory.DAY, 0, 100)
    df2 = client.get_index_bars(Market.SZ, "399001", KlineCategory.DAY, 0, 100)
```

### 2. 分页获取大量数据

单次最多返回800条，需要更多数据时使用分页：

```python
def get_all_bars(client, market, code, category, total=2000):
    """获取超过800条的K线数据"""
    result = []
    start = 0
    while start < total:
        count = min(800, total - start)
        df = client.get_index_bars(market, code, category, start, count)
        if df.empty:
            break
        result.append(df)
        start += count
    
    return pd.concat(result, ignore_index=True) if result else pd.DataFrame()
```

### 3. 批量获取实时行情

使用 `get_security_quotes` 一次获取多只股票：

```python
# 效率高：一次请求
stocks = [(Market.SH, f"{i:06d}") for i in range(600000, 600010)]
df = client.get_security_quotes(stocks)

# 效率低：多次请求（避免）
for market, code in stocks:
    df = client.get_security_quotes([(market, code)])
```

### 4. 缓存策略

- `get_security_list_all()` 自带24小时缓存
- 历史K线数据可以本地缓存，只更新最新的
- 实时数据根据业务需求设置合理的刷新频率

## 常用指数代码

| 代码 | 市场 | 名称 |
|------|------|------|
| 000001 | SH | 上证指数 |
| 000016 | SH | 上证50 |
| 000300 | SH | 沪深300 |
| 000905 | SH | 中证500 |
| 000852 | SH | 中证1000 |
| 399001 | SZ | 深证成指 |
| 399006 | SZ | 创业板指 |
| 399005 | SZ | 中小板指 |
| 931468 | SH | 红利低波指数 |
| 931373 | SH | 恒生港股通高股息低波动指数 |

## 注意事项

1. **频率限制**: 通达信服务器对请求频率有限制，建议单连接 QPS 不超过 10
2. **时间范围**: 不同周期的K线数据历史长度不同，日K通常有10年以上历史
3. **交易时间**: 实时数据仅在交易时段更新（9:30-11:30, 13:00-15:00）
4. **节假日**: 非交易日无法获取当日数据
5. **连接稳定性**: 建议实现自动重连机制，TdxClient 已内置重试逻辑

## 与其他数据源对比

| 特性 | easy_tdx | akshare | efinance | mootdx |
|------|----------|---------|----------|---------|
| 免费 | ✅ | ✅ | ✅ | ✅ |
| 指数数据 | ✅ | ✅ | ✅ | ✅ |
| 分时数据 | ✅ | ✅ | ✅ | ✅ |
| 速度 | 快 | 中 | 快 | 快 |
| 稳定性 | 高 | 中 | 高 | 中 |
| 历史数据 | 完整 | 完整 | 完整 | 完整 |
| 依赖 | 少 | 多 | 中 | 中 |

