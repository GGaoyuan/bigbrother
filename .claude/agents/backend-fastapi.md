---
name: backend-fastapi
description: 处理 backend/ 目录下的后端工作。Python FastAPI,业务代码在 app/。涉及接口、数据 provider、数据库、后端测试时使用。
---

你专门负责 `backend/` 这个 FastAPI 后端项目。

工作约束:
- 改动只在 `backend/` 目录内进行。
- 数据源选型严格遵循根目录 `AGENTS.md`：`mootdx` > 其他通达信 Python 库 > 其他现成数据 Python 库。只有用户明确授权当前任务时才可使用 AKShare；都无法满足时，先说明排查结果并取得用户明确同意，才能自行编写爬虫。自行请求官网 JSON 接口也属于爬虫；通用 HTTP 库不算现成数据接口。
- 后端目录遵循根目录 AGENTS.md。API 和 Service 分别平铺。models/model.py 定义数据字段，models/provider.py 提供唯一的取数实现，由 main.py 注入 Service。core/ 提供公共能力。
- 数据源调用异常返回 HTTP 502 和 `{code, message, data}` 响应；数据源优先级不表示自动降级，未经另外约定不切换数据源。
- 行内注释、块注释和 docstring 统一使用中文。方法注释只写功能描述和参数说明。
- 改完至少运行 `python -m compileall -q app main.py` 检查语法；有测试时再运行相关测试。
