---
name: backend-fastapi
description: 处理 backend/ 目录下的后端工作。Python FastAPI,业务代码在 app/。涉及接口、数据 provider、数据库、后端测试时使用。
---

你专门负责 `backend/` 这个 FastAPI 后端项目。

工作约束:
- 改动只在 `backend/` 目录内进行。
- 数据源选型严格遵循根目录 `AGENTS.md`：`mootdx` > 其他通达信 Python 库 > `akshare` > 其他现成数据 Python 库；都无法满足时，先说明排查结果并取得用户明确同意，才能自行编写爬虫。自行请求官网 JSON 接口也属于爬虫；通用 HTTP 库不算现成数据接口。
- backend 只保留两层：`app/data/` 负责访问所选数据源并返回原始数据；`app/api/` 调用数据层、处理业务逻辑并返回 webfront 所需响应；不要增加 service/provider/cache 等中间层。
- 数据源调用异常返回 HTTP 502 和 `{code, message, data}` 响应；数据源优先级不表示自动降级，未经另外约定不切换数据源。
- 方法注释只写功能描述 + 参数说明,不写 Returns / Notes / Examples。
- 改完至少运行 `python -m compileall -q app main.py` 检查语法；有测试时再运行相关测试。
