# Provider 接口目录

`app/providers/` 下所有 provider 文件的接口索引。新增/修改 provider 接口时**必须**同步本文件，详见 `provider-doc-sync` skill。

> 字段命名见 `app/field_map.md`，文件组织规范见 `provider-organization` skill。

---

## individual_net_inflow.py

返回 model：`ThsIndividualNetInflow`
数据源：akshare（同花顺）
用途：同花顺全市场个股资金流向（即时快照）

| 方法 | 数据源接口 | 参数 | 返回 | 说明 |
| --- | --- | --- | --- | --- |
| get_ths_individual_net_inflow | ak.stock_fund_flow_individual(symbol="即时") | 无 | List[ThsIndividualNetInflow] | 全市场个股流入/流出/净额/成交额（已解析单位） |

---

## sw_industry_component.py

返回 model：`SwIndustryComponent`
数据源：akshare（申万官方）
用途：申万行业成分股基础信息（代码、名称、权重、纳入日期）

| 方法 | 数据源接口 | 参数 | 返回 | 说明 |
| --- | --- | --- | --- | --- |
| get_sw_index_component | ak.index_component_sw | symbol: str（行业代码，不含 .SI） | List[SwIndustryComponent] | 单个申万行业的成分股列表 |

---

## sw_industry_index.py

返回 model：`SwIndustryIndex`
数据源：akshare（申万官方）
用途：申万一/二/三级行业指数信息（代码、名称、上级行业、估值指标）

| 方法 | 数据源接口 | 参数 | 返回 | 说明 |
| --- | --- | --- | --- | --- |
| get_sw_index_first_info | ak.sw_index_first_info | 无 | List[SwIndustryIndex] | 申万一级行业指数信息 |
| get_sw_index_second_info | ak.sw_index_second_info | 无 | List[SwIndustryIndex] | 申万二级行业指数信息 |
| get_sw_index_third_info | ak.sw_index_third_info | 无 | List[SwIndustryIndex] | 申万三级行业指数信息 |

---

## sw_industry_third_cons.py

返回 model：`SwIndustryThirdCons`
数据源：akshare（乐咕乐股）
用途：申万三级行业成分股的详细信息（估值、市值、业绩同比等）

| 方法 | 数据源接口 | 参数 | 返回 | 说明 |
| --- | --- | --- | --- | --- |
| get_sw_index_third_cons | ak.sw_index_third_cons | symbol: str（三级行业代码，需带 .SI） | List[SwIndustryThirdCons] | 单个三级行业成分股的全字段信息 |
