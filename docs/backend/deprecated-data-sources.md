# 禁用数据源清单

## 已禁用的数据源库

以下三个数据源库已被禁止使用：
- `akshare`
- `efinance`
- `adata`

## 原因

用户明确要求禁用这三个库，所有数据源必须使用 `easy_tdx` 或 `mootdx`。

## 已标记为 DEPRECATED 的文件

以下文件使用了禁用的数据源，已添加 `# DEPRECATED:` 标记，需要迁移：

1. `backend/app/providers/hotlist.py` - 使用 akshare
2. `backend/app/providers/sw_industry_index.py` - 使用 akshare
3. `backend/app/providers/sector_intraday.py` - 使用 efinance
4. `backend/app/providers/index_data.py` - 使用 akshare
5. `backend/app/providers/news_macro.py` - 使用 akshare
6. `backend/app/providers/board_data.py` - 使用 akshare
7. `backend/app/providers/sw_industry_third_cons.py` - 使用 akshare
8. `backend/app/providers/market_breadth.py` - 使用 akshare
9. `backend/app/providers/individual_net_inflow.py` - 使用 akshare
10. `backend/app/providers/sw_industry_component.py` - 使用 akshare
11. `backend/app/providers/capital_data.py` - 使用 akshare

## 已修复的文件

### ✅ backend/app/providers/index_kline.py
- **修复前**: 使用 efinance 作为降级方案
- **修复后**: 只使用 easy_tdx MacClient
- **API**: `client.get_stock_kline(market, code, period, start, count)`
- **测试状态**: 待测试（需要后端重启）

### ✅ backend/app/providers/volume_kline.py
- **状态**: 已经使用 easy_tdx MacClient，无需修改

## 迁移指南

使用 easy_tdx 或 mootdx 替代禁用的库：

### easy_tdx 客户端选择

1. **MacClient** - Mac 行情协议（推荐，已在项目中使用）
   - 获取 K 线：`get_stock_kline(market, code, period, start, count)`
   - 获取报价：`get_stock_quotes(stocks)`
   - 获取板块：`get_board_list()`

2. **TdxClient** - 标准 TDX 协议
   - 获取股票 K 线：`get_security_bars(market, code, category, start, count)`
   - 获取指数 K 线：`get_index_bars(market, code, category, start, count)`

3. **UnifiedTdxClient** - 统一客户端（内部路由到 MacClient 或 MacExClient）
   - A 股方法代理到 MacClient
   - 扩展市场（美股、港股等）代理到 MacExClient

### 复用已有客户端

项目中已有全局单例 MacClient：
```python
from app.providers.client.easy_tdx_client import get_mac_client

client = get_mac_client()
df = client.get_stock_kline(market, code, period, start, count)
```

### 市场代码

- 0 = 深圳市场
- 1 = 上海市场
- 2 = 北京市场

### 周期枚举

```python
from easy_tdx import Period

Period.MIN_1      # 1分钟
Period.MIN_5      # 5分钟
Period.MIN_30     # 30分钟
Period.DAILY      # 日线
Period.WEEKLY     # 周线
Period.MONTHLY    # 月线
```

## 下一步工作

需要逐个迁移上述 11 个 DEPRECATED 文件，将数据源从 akshare/efinance/adata 切换到 easy_tdx/mootdx。
