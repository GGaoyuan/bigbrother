# 桌面端 API 文档（v2）

> **定位**：供 `desktop/` Tauri 桌面项目使用  
> **前缀**：`/api/v2`  
> **v1 区别**：v1 面向市场分析（dashboard、北向、龙虎榜等），v2 面向桌面业务基础数据

---

## 鉴权

与 v1 相同，请求 Header 需携带：

| Header | 值（beta） |
|--------|------------|
| `token` | `gaoyuanzuishuai` |
| `uid` | `1993` |

---

## 接口列表

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/v2/fundation/realtime-sectors` | POST | 东财板块实时行情 |
| `/api/v2/fundation/sw-industry` | POST | 申万一/二/三级行业 |
| `/api/v2/fundation/sw-stock-industry` | POST | 全市场股票行业归属 |
| `/api/v2/market-cap/total` | POST | A股总市值走势（申万A指代理，DAILY 缓存） |
| `/api/v2/market-cap/industry-tree` | POST | 申万行业分类树（WEEKLY 缓存） |
| `/api/v2/market-cap/industry-trend` | POST | 单行业指数走势，用于图表叠加（按行业 DAILY 缓存） |
| `/api/v2/market-cap/total-volume` | POST | A股总成交额走势（申万A指成交额代理，DAILY 缓存） |
| `/api/v2/market-cap/industry-volume` | POST | 单行业成交额走势，用于图表叠加（按行业 DAILY 缓存） |
| `/api/v2/sector-flow/ranking` | POST | 今日板块资金流入/流出排行 + 全量列表（DAILY 缓存） |
| `/api/v2/sector-flow/trend` | POST | 单板块资金流历史走势，用于图表叠加（按板块 DAILY 缓存） |

---

## 接口详情

### `POST /api/v2/fundation/realtime-sectors`

板块实时行情。

```bash
curl -X POST http://127.0.0.1:8000/api/v2/fundation/realtime-sectors \
  -H "token: gaoyuanzuishuai" -H "uid: 1993" \
  -H "Content-Type: application/json" \
  -d '{"type": 3}'
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| type | int | 3 | 1=行业，2=概念，3=全部 |

### `POST /api/v2/fundation/sw-industry`

申万行业分类，返回 `first` / `second` / `third` 三级列表。

```bash
curl -X POST http://127.0.0.1:8000/api/v2/fundation/sw-industry \
  -H "token: gaoyuanzuishuai" -H "uid: 1993"
```

### `POST /api/v2/fundation/sw-stock-industry`

全市场股票与申万行业归属（首次约 60s，之后走缓存）。

```bash
curl -X POST http://127.0.0.1:8000/api/v2/fundation/sw-stock-industry \
  -H "token: gaoyuanzuishuai" -H "uid: 1993"
```

### `POST /api/v2/market-cap/total`

A股总市值走势，以申万A指（801003）日线作为代理序列，DAILY 缓存。

```bash
curl -X POST http://127.0.0.1:8000/api/v2/market-cap/total \
  -H "token: gaoyuanzuishuai" -H "uid: 1993"
```

返回：`{ symbol, name, points: [{ time: "YYYY-MM-DD", value }] }`

### `POST /api/v2/market-cap/industry-tree`

申万一/二/三级行业分类树，复用 `sw-industry` 数据，WEEKLY 缓存。返回 `first` / `second` / `third` 三级列表，每项含 `sw_industry_code`、`sw_industry_name`、`sw_parent_industry`、`sw_component_count`。

```bash
curl -X POST http://127.0.0.1:8000/api/v2/market-cap/industry-tree \
  -H "token: gaoyuanzuishuai" -H "uid: 1993"
```

### `POST /api/v2/market-cap/industry-trend`

单个申万行业指数走势，用于叠加到总市值图表。按行业代码分别 DAILY 缓存。

```bash
curl -X POST http://127.0.0.1:8000/api/v2/market-cap/industry-trend \
  -H "token: gaoyuanzuishuai" -H "uid: 1993" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "801010.SI"}'
```

| 参数 | 类型 | 说明 |
|------|------|------|
| symbol | str | 申万指数代码，带或不带 `.SI` 后缀均可 |

返回：`{ symbol, points: [{ time, value }] }`

---

## 目录结构

```
app/api/v2/
├── router.py      # v2 路由聚合入口
└── fundation.py   # 桌面端基础数据
```

新增桌面端接口时，在 `app/api/v2/` 下建模块，并在 `router.py` 中 `include_router`。
