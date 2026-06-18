# A 股市场分析 API 文档

> **v1**：市场分析专用（指数、宽度、板块、资金、消息面）  
> **v2**：桌面端专用（基础行情、行业分类等）→ 见 [`API_v2.md`](./API_v2.md)

> 测试时间：2026-06-15  
> 测试环境：macOS + Python 3.12 + `.venv`  
> 完整机器可读结果见 [`api_test_results.json`](./api_test_results.json)

---

## 1. 快速开始

### 启动服务

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 鉴权 Header（所有业务接口必填）

| Header | 值（beta） |
|--------|------------|
| `token` | `gaoyuanzuishuai` |
| `uid` | `1993` |

### 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

- `code=200`：成功
- `code=500`：业务异常（多为外部数据源失败）
- `code=502`：未登录 / 鉴权失败

---

## 2. 接口总览

| 分类 | 路径 | 方法 | 测试状态 | 说明 |
|------|------|------|----------|------|
| 基础 | `/` | GET | ✅ 通过 | 服务信息 |
| 基础 | `/health` | GET | ✅ 通过 | 健康检查 |
| 指数 | `/api/v1/market/index/core` | POST | ⚠️ 网络 | 三大指数日K + 均线/趋势 |
| 指数 | `/api/v1/market/index/spot` | POST | ⚠️ 网络 | 实时指数快照 |
| 指数 | `/api/v1/market/index/style` | POST | ⚠️ 网络 | 大小盘风格对比 |
| 指数 | `/api/v1/market/index/hist` | POST | ⚠️ 网络 | 单指数历史日K |
| 宽度 | `/api/v1/breadth/volume` | POST | ⚠️ 网络 | 两市成交统计 |
| 宽度 | `/api/v1/breadth/limit-pools` | POST | ✅ 通过 | 涨跌停/炸板/强势股池 |
| 宽度 | `/api/v1/breadth/fund-flow-rank` | POST | ⚠️ 网络 | 个股资金流排名 |
| 板块 | `/api/v1/sector/realtime` | POST | ⚠️ 网络 | 东财行业/概念实时行情 |
| 板块 | `/api/v1/sector/fund-flow` | POST | ⚠️ 网络 | 板块资金流向 |
| 板块 | `/api/v1/sector/ths-fund-flow` | POST | ⚠️ 禁用 | 同花顺资金流（macOS 环境禁用） |
| 板块 | `/api/v1/sector/sw-industry` | POST | ✅ 通过 | 申万一/二/三级行业 |
| 板块 | `/api/v1/sector/sw-stock-industry` | POST | ✅ 通过 | 全市场股票行业归属（慢，~60s） |
| 资金 | `/api/v1/capital/northbound` | POST | ✅ 通过 | 北向资金 |
| 资金 | `/api/v1/capital/margin` | POST | ✅ 通过 | 两融余额 |
| 资金 | `/api/v1/capital/dragon-tiger` | POST | ✅ 通过 | 龙虎榜 |
| 资金 | `/api/v1/capital/market-flow` | POST | ⚠️ 网络 | 大盘资金流向 |
| 消息 | `/api/v1/news/overview` | POST | ✅ 服务可用 | 新闻/宏观/海外指数 |
| 汇总 | `/api/v1/analysis/dashboard` | POST | ✅ 通过 | 全量分析面板 |
| 透传 | `/api/v1/forward` | POST | ✅ 通过 | 直接调用 akshare/efinance |

**图例：**
- ✅ 通过：返回有效数据
- ⚠️ 网络：接口逻辑正常，但当前环境访问东财/新浪失败（代理或限流）
- ⚠️ 禁用：因 `py_mini_racer` 在 macOS 上不稳定，主动降级返回空数据

---

## 3. 接口详情

### 3.1 基础

#### `GET /`

```bash
curl http://127.0.0.1:8000/
```

#### `GET /health`

```bash
curl http://127.0.0.1:8000/health
```

---

### 3.2 指数行情 `/api/v1/market`

#### `POST /api/v1/market/index/core`

三大指数（上证/深成/创业板）日K，附带 MA5~MA250、支撑/压力位、trend 字段。

```bash
curl -X POST http://127.0.0.1:8000/api/v1/market/index/core \
  -H "token: gaoyuanzuishuai" -H "uid: 1993"
```

返回示例结构：

```json
{
  "sh": [{"index_code":"000001","close":3400.5,"ma5":3380,"trend":"bull","datasource":"EAST_MONEY"}],
  "sz": [],
  "cyb": []
}
```

缓存策略：`DAILY`（自然日）

#### `POST /api/v1/market/index/spot`

实时指数快照。缓存：`NONE`（实时）

#### `POST /api/v1/market/index/style`

沪深300 / 中证500 / 中证1000 / 中证2000 最新涨跌对比，含 `large_vs_small_spread`。

#### `POST /api/v1/market/index/hist`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/market/index/hist \
  -H "token: gaoyuanzuishuai" -H "uid: 1993" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"000001","index_name":"上证指数"}'
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| symbol | string | 000001 | 指数代码 |
| index_name | string | "" | 指数名称 |
| start_date | string | 近250天 | YYYYMMDD |
| end_date | string | 今天 | YYYYMMDD |

---

### 3.3 市场宽度 `/api/v1/breadth`

#### `POST /api/v1/breadth/volume`

两市成交快照 + 上交所/深交所市场总貌。

测试通过时返回：

```json
{
  "turnover_snapshot": {"total_turnover": 1.2e12, "stock_count": 5200},
  "sse_summary": [],
  "szse_summary": []
}
```

#### `POST /api/v1/breadth/limit-pools`

涨跌停池统计（自动回退最近交易日）。

```bash
curl -X POST http://127.0.0.1:8000/api/v1/breadth/limit-pools \
  -H "token: gaoyuanzuishuai" -H "uid: 1993" \
  -H "Content-Type: application/json" \
  -d '{}'
```

测试通过数据量示例：

```json
{
  "limit_up": 145,
  "limit_down": 3,
  "broken_limit": 43,
  "strong": 176
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| date | string | 可选，YYYYMMDD |

#### `POST /api/v1/breadth/fund-flow-rank`

```json
{"indicator": "今日"}
```

`indicator` 可选：`今日` / `3日` / `5日` / `10日`

---

### 3.4 板块 `/api/v1/sector`

#### `POST /api/v1/sector/realtime`

```json
{"type": 3}
```

| type | 含义 |
|------|------|
| 1 | 仅行业 |
| 2 | 仅概念 |
| 3 | 全部 |

#### `POST /api/v1/sector/fund-flow`

```json
{"indicator": "今日", "sector_type": "行业资金流"}
```

`sector_type` 也可传 `概念资金流`。

#### `POST /api/v1/sector/ths-fund-flow`

同花顺行业/概念资金流。**当前 macOS 环境默认返回空数据**，避免 `py_mini_racer` 崩溃：

```json
{
  "ths_concept": [],
  "ths_industry": [],
  "error": "ths_api_disabled_on_current_platform"
}
```

#### `POST /api/v1/sector/sw-industry`

申万一级(31) / 二级(131) / 三级(336) 行业列表。缓存：`WEEKLY`

#### `POST /api/v1/sector/sw-stock-industry`

全市场 5000+ 只股票的行业归属。首次拉取约 60 秒。缓存：`MONTHLY`

---

### 3.5 资金结构 `/api/v1/capital`

#### `POST /api/v1/capital/northbound`

北向资金实时摘要 + 历史（约 2689 条）。

#### `POST /api/v1/capital/margin`

沪深两融余额（SSE 历史 + SZSE 最近交易日）。

#### `POST /api/v1/capital/dragon-tiger`

```json
{"start_date": "20260615", "end_date": "20260615"}
```

不传日期时默认当天。

#### `POST /api/v1/capital/market-flow`

大盘超大单/大单/中单/小单资金流向。

---

### 3.6 消息面 `/api/v1/news`

#### `POST /api/v1/news/overview`

返回：

```json
{
  "news": [],
  "macro_operation": [],
  "lpr": [],
  "us_indices": [],
  "hot_concepts": []
}
```

- `news`：东财财经新闻
- `macro_operation`：央行公开市场操作（`macro_china_bank_financing`）
- `lpr`：LPR 利率
- `us_indices`：美股三大指数
- `hot_concepts`：问财热点（默认关闭，避免超时）

---

### 3.7 全量分析 `/api/v1/analysis`

#### `POST /api/v1/analysis/dashboard`

**推荐入口**：一次获取 spec 所需的全部核心数据。

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analysis/dashboard \
  -H "token: gaoyuanzuishuai" -H "uid: 1993"
```

返回结构：

```json
{
  "index": {"core_daily": {}, "spot": [], "style_compare": {}},
  "breadth": {"volume": {}, "limit_pools": {}, "fund_flow_rank": []},
  "sector": {"realtime": {}, "industry_fund_flow": [], "ths_fund_flow": {}, "sw_industry": {}},
  "capital": {"northbound": {}, "margin": {}, "dragon_tiger": [], "market_flow": []},
  "news": {}
}
```

特性：
- 各子模块并行拉取
- 单模块失败不阻断整体（`return_exceptions=True`）
- 耗时约 8~70 秒（取决于缓存命中）

---

### 3.8 透传 `/api/v1/forward`

直接调用 akshare / efinance 函数，用于调试新接口。

```bash
curl -X POST http://127.0.0.1:8000/api/v1/forward \
  -H "token: gaoyuanzuishuai" -H "uid: 1993" \
  -H "Content-Type: application/json" \
  -d '{"source":"akshare","fn":"stock_sse_summary","param":{}}'
```

| 参数 | 说明 |
|------|------|
| source | `akshare` 或 `efinance` |
| fn | 函数名 |
| param | 参数字典 |

---

## 4. 缓存策略

| 策略 | 刷新规则 | 典型接口 |
|------|----------|----------|
| `NONE` | 每次实时拉取 | 指数 spot、板块 realtime |
| `DAILY` | 次日 0:00 后可刷新 | 北向、龙虎榜、涨跌停池 |
| `WEEKLY` | 下周一 0:00 后可刷新 | 申万行业列表 |
| `MONTHLY` | 下月 1 日 0:00 后可刷新 | 股票行业归属 |

缓存文件目录：`app/cache/data/`（CSV 存列表，JSON 存复杂对象）

---

## 5. 测试方法与结果

### 运行测试

```bash
cd backend
source .venv/bin/activate
pip install httpx   # TestClient 依赖
python test_api_endpoints.py
```

### 本次测试摘要（21 个接口）

| 结果 | 数量 | 接口 |
|------|------|------|
| ✅ 通过 | 10 | `/`, `/health`, `limit-pools`, `sw-industry`, `sw-stock-industry`, `northbound`, `margin`, `dragon-tiger`, `analysis/dashboard`, `forward` |
| ⚠️ 网络失败 | 9 | 所有东财实时类（指数/板块/成交/资金流等） |
| ⚠️ 环境限制 | 2 | `ths-fund-flow`（已降级）、`news/overview`（服务层正常） |

### 常见失败原因

1. **Connection aborted / RemoteDisconnected**  
   东财 `push2.eastmoney.com` 在当前网络/代理下不可达。  
   处理：检查 Clash/VPN，或交易时段重试。

2. **py_mini_racer 崩溃**  
   同花顺相关 akshare 接口在 macOS 上不稳定。  
   处理：`ths-fund-flow` 已默认返回空数据。

3. **非交易日空数据**  
   涨跌停池、深市两融等接口在非交易日可能为空。  
   处理：已内置最近交易日回退逻辑。

---

## 6. 架构对应

```
api/v1/*.py          → HTTP 入口
app/service/*.py     → 业务编排 + 缓存策略
app/providers/*.py   → akshare 取数 + 字段映射
app/cache/           → 文件缓存（CSV/JSON）
```

字段标准见 [`field_map.md`](./field_map.md)，Provider 索引见 [`provider.md`](./provider.md)，数据需求见 [`a_stock_analysis_data_spec.md`](./a_stock_analysis_data_spec.md)。

---

## 7. 推荐调用顺序

1. **日常复盘**：`POST /api/v1/analysis/dashboard`
2. **盘中快速看指数**：`POST /api/v1/market/index/spot`
3. **涨停梯队**：`POST /api/v1/breadth/limit-pools`
4. **北向 + 龙虎榜**：`POST /api/v1/capital/northbound` + `dragon-tiger`
5. **行业归属查询**：`POST /api/v1/sector/sw-stock-industry`（有缓存后很快）
6. **调试新 akshare 接口**：`POST /api/v1/forward`
