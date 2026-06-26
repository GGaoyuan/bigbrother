# BigBrother 项目记忆文档

> 本文档记录项目的架构规则、开发规范、注意事项等重要信息

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
1. **easy_tdx** （最优先）
2. **mootdx**
3. **其他**（efinance、akshare 等）

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
- 优先使用 easy_tdx 和 mootdx 数据源
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

### 2026-06-26
- **Provider 职责明确**：负责数据获取 + 缓存/持久化
- **当前临时要求**：新增的指数 K 线和成交量分布接口暂不加缓存（实时性优先）
- 数据源优先级：easy_tdx > mootdx > 其他
- 文档命名规范：添加前缀区分模块（backend-、desktop- 等）
