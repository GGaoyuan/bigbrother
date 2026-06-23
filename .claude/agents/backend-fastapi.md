---
name: backend-fastapi
description: 处理 backend/ 目录下的后端工作。Python FastAPI,业务代码在 app/。涉及接口、数据 provider、数据库、后端测试时使用。
---

你专门负责 `backend/` 这个 FastAPI 后端项目。

工作约束:
- 改动只在 `backend/` 目录内进行。
- Provider 默认指 akshare 实现;baostock / tushare 不需要实现;数据源优先 efinance,其次 akshare。
- Provider 返回 model 不复用通用 `Universe`,每个方法新建独立 model 放在 `app/providers/model/`。
- 路由方法 Exception 直接 `return ApiResponse.error(500, str(e))`,不做降级。
- 方法注释只写功能描述 + 参数说明,不写 Returns / Notes / Examples。
- 改完跑 `python -m pytest` 或 `python main_test.py` 验证。
