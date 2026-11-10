# BigBrother 项目记忆文档

> 本文档记录项目的架构规则、开发规范、注意事项等重要信息
> 当前持久规则以根目录 `AGENTS.md` 为准；当前两层后端架构和功能状态见 `prd/v1.md`。本文中的 Provider/Service 结构为历史记录。

## 一、架构规范

### Backend 架构

#### 分层架构
- **Provider 层**：数据获取与持久化
  - 职责：
    1. 对接外部数据源（akshare、efinance、mootdx、easy_tdx）
    2. **负责缓存/持久化数据**（使用 `@cached_json` 等装饰器）
    3. 返回结构化数据给 Service 层
  - 缓存策略：根据数据特点决定是否缓存（实时数据不缓存，日线等可缓存）
  - **当前临时要求**：新增的指数 K 线和成交量分布接口暂不加缓存
  
- **Service 层**：业务逻辑编排
  - 职责：调用 Provider，组装业务数据
  - 继承 `BaseService[T]`，实现 `_execute()` 方法
  - 不处理缓存（缓存在 Provider 层）
  
- **API 层**：路由和请求处理
  - 调用 Service，处理异常
  - 异常直接返回 `ApiResponse.error(500, str(e))`

#### 数据源优先级
1. **mootdx**（最优先）
2. **其他通达信 Python 库**（如 easy_tdx、pytdx）
3. **akshare**
4. **其他提供数据接口的 Python 库**
5. 以上均无法满足时，说明排查结果，**先取得用户明确同意，再自行编写爬虫**。

自行请求官网 JSON 接口也属于爬虫；仅使用 requests/httpx/urllib 等通用 HTTP 库不算现成数据接口。本顺序用于选型，不代表运行时自动降级。该规则在项目新会话中继续适用。

### 代码规范

#### 注释规范
- 方法注释只写：功能描述 + 参数说明
- 不写：Returns / Notes / Examples

#### Provider Model
- 每个 Provider 方法新建独立 model
- 放在 `backend/app/providers/model/`
- 不使用通用 `Universe` 模型

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

## 四、开发注意事项

### Provider 开发
- **负责缓存/持久化**：根据数据特点使用 `@cached_json` 等装饰器
- 数据源选型遵循 `mootdx > 其他通达信 Python 库 > akshare > 其他现成数据 Python 库`；都无法满足时先取得用户同意再写爬虫。
- 为每个返回类型创建独立的 Pydantic Model
- **当前临时要求**：新增的指数 K 线和成交量分布接口暂不加缓存（实时性优先）

### Service 开发
- 继承 `BaseService[T]`
- 实现 `async def _execute(self) -> T`
- 不处理缓存逻辑

### API 开发
- 路由方法遇到 Exception 直接返回 `ApiResponse.error(500, str(e))`
- 不做降级处理（除非特别说明）

## 五、历史决策记录

### 2026-11-10
- 将数据源优先级统一为 `mootdx > 其他通达信 Python 库 > akshare > 其他现成数据 Python 库`。
- 自行写爬虫前必须先检查上述库并取得用户明确同意，官网 JSON 接口同样适用。
- 规则保存到根目录 `AGENTS.md` 并同步后端代理配置，供项目后续新会话继续使用；替代此前数据源限制。

### 2026-06-26
- **Provider 职责明确**：负责数据获取 + 缓存/持久化
- **当前临时要求**：新增的指数 K 线和成交量分布接口暂不加缓存（实时性优先）
- 当时的数据源优先级为 easy_tdx > mootdx > 其他；已被 2026-11-10 的规则取代。
- 文档命名规范：添加前缀区分模块（backend-、desktop- 等）
