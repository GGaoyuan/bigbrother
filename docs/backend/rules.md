# 规则

当前数据源规则见根目录 `AGENTS.md`：mootdx > 其他通达信 Python 库 > akshare > 其他现成数据 Python 库；都无法满足时，先取得用户明确同意再自行写爬虫，包括自行请求官网 JSON 接口。

以下为历史架构约定；当前后端采用 data/API 两层结构，以 `prd/v1.md` 为准。

注释要写清楚
service/bean/FIELED.md的内容，将重名的字段都合并，只保留一个
api/v1下的接口，只负责调用对应的service中的内容，

provider中的ef_provider只负责调用ef框架的内容，
    ef_provider下的bean只负责将ef框架的返回值，转义成对象和字段，字段的名称严格按照 service/bean/FIELED.md的内容

provider中的ak_provider只负责调用ak框架的内容，
    ak_provider下的bean只负责将ak框架的返回值，转义成对象和字段，字段的名称严格按照 service/bean/FIELED.md的内容    

在service中完成api/v1中调用者对应的逻辑，最后将返回值封装成bean，放在service/bean文件夹内，且要多加一个数据来源的字段


---
