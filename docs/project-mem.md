# BigBrother 项目记忆文档

> 当前持久规则见根目录 `AGENTS.md`，功能状态见 `prd/v1.md`。

## 一、架构规范

- `api/` 每条业务路由一个文件，路由和业务逻辑放在同一文件，直接调用 Provider。
- `models/` 按数据类型分包。各分类的 `model.py` 定义字段，`provider.py` 是该分类唯一的取数实现。成交量分布由 API 模块计算，只定义模型。
- `core/` 提供公共基础设施。`main.py` 组装应用、中间件和路由。
- 数据源选型先查 mootdx，再查其他通达信库和其他现成库。AKShare 只在用户明确授权的任务范围内使用。自行请求公开网站或交易所 JSON 接口须先获得用户同意。
- 同一种 Model 能用一个库覆盖需求时只保留该实现。股票资料和 K 线使用 easy_tdx，交易日历读取 XSHG 离线日历。各周期前复权由 Provider 传 `Adjust.QFQ` 直接取得，API 校验和使用这些价格。
- 优先保留当前业务需要的最简单实现，利用行情库已有参数和返回值，避免重复算法与多余模块。
- 业务数据和计算结果默认不缓存。接口每次重新取数和计算，只有用户明确要求时才引入缓存。

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

### 2026-11-27

- 删除后端行情、交易日历与成交量分布缓存，并将桌面端行业走势改为每次选中时重新请求。
- 删除独立 Service 层，股票资料、K 线和成交量分布的业务逻辑并入对应 API 文件。
- K 线图和成交量分布直接使用通达信返回的前复权行情，移除应用内复权公式及专用除权取数。
- 业务路由及 Service 一一对应，复权因子获取归入 K 线 Service，图表和成交量分布共用。
- 将后端收为 API、Service、Models、Core 四层，按 K 线、股票资料、除权事件、交易日历和成交量分布组织模型。每类取数实现放在同一分类的 `provider.py`。
- K 线合并为 easy_tdx 单一取数实现，通达信公共主站和腾讯的 K 线适配器移除。

### 2026-11-26

- API 与 Service 按文件平铺，Model 和 Data 按数据类型合并组织。
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
