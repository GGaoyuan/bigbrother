# BigBrother 项目记忆文档

> 当前持久规则见根目录 `AGENTS.md`，功能状态见 `prd/v1.md`。

## 一、架构规范

- `api/` 接收 HTTP 参数、调用 Service、生成独立响应模型和统一错误响应。
- `services/` 负责股票查询、K 线、统一前复权和成交量分布，以及各自的缓存策略。
- `data/` 按能力提供 K 线、股票信息、除权事件和交易日历，向上返回标准模型。
- `models/` 定义内部数据结构和取数协议，`core/` 提供基础设施。Data 具体实现在 `main.py` 注入 Service。
- 数据源选型先查 mootdx，再查其他通达信库和其他现成库。AKShare 只在用户明确授权的任务范围内使用。自行请求公开网站或交易所 JSON 接口须先获得用户同意。

## 二、文档规范

### 命名规则
- Backend 文档：`backend-` 前缀（如 `backend-架构说明.md`）
- Desktop 文档：`desktop-` 前缀（如 `desktop-组件设计.md`）
- Webfront 文档：`webfront-` 前缀
- 通用文档：无前缀或 `project-` 前缀

### 文档位置
- 项目记忆和规则：`docs/project-mem.md`（本文档）
- 后端文档：`docs/backend/`
- PRD 文档：`prd/`

## 三、项目目录说明

- `backend/`: FastAPI 后端
- `webfront/`: Web 前端
- `desktop/`: 桌面端（推测）
- `docs/`: 文档目录
- `prd/`: 产品需求文档

## 四、历史决策记录

### 2026-11-26

- 后端迁移到 API、Service、Model、Data、Core 五层。Model 持有数据契约，Data 接入外部数据。方案与缓存策略见 `docs/backend/backend-stocks-api.md`。
- 移除 AKShare，交易日核验改用 XSHG 离线日历。

### 2026-11-10
- 将数据源优先级统一为 `mootdx > 其他通达信 Python 库 > akshare > 其他现成数据 Python 库`。
- 自行写爬虫前必须先检查上述库并取得用户明确同意，官网 JSON 接口同样适用。
- 规则保存到根目录 `AGENTS.md` 并同步后端代理配置，供项目后续新会话继续使用；替代此前数据源限制。

### 2026-06-26
- **Provider 职责明确**：负责数据获取 + 缓存/持久化
- **当前临时要求**：新增的指数 K 线和成交量分布接口暂不加缓存（实时性优先）
- 当时的数据源优先级为 easy_tdx > mootdx > 其他；已被 2026-11-10 的规则取代。
- 文档命名规范：添加前缀区分模块（backend-、desktop- 等）
