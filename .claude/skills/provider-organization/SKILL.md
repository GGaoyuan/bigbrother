---
name: provider-organization
description: FastAPI 项目（FastAPI/）中 provider 层的组织规范。在 app/providers/ 下新增、修改或重构数据获取代码时使用。规则：所有外部数据框架（akshare/efinance/baostock/tushare/qstock 等）的调用都写在 app/providers/ 下；按返回的 model 类型分文件，同 model 的方法合并到一个文件，不同 model 各自一个文件；model 字段名遵循 stock-field-mapping skill 的统一命名，不同含义字段必须用不同英文名，避免重名歧义；新增/修改字段后必须同步到 FastAPI/app/field_map.md 总对照表。Examples："新增一个获取概念板块的接口"、"重构 provider 文件结构"、"akshare 这个新接口写哪个文件"、"两个 provider 返回字段冲突怎么办"、"加了新字段忘了同步对照表"。
---

# Provider 组织规范

约束 `FastAPI/app/providers/` 下数据获取代码的目录、文件、命名结构，让 service 层调用稳定一致。

## 核心规则

### 1. 所有外部数据获取代码都放在 `app/providers/`

凡是调用 `akshare` / `efinance` / `baostock` / `tushare` / `qstock` / `adata` / `easyquotation` 等三方库拿数据的代码，**统一写在 `app/providers/` 下**。Service 层、controller 层禁止直接 `import akshare as ak` 之类的调用，必须经过 provider。

### 2. 按返回 model 类型分文件

文件命名 = model 含义。**同一个返回 model 的所有方法写在同一个文件里；不同 model 各占一个文件。**

#### 已有示例

| 文件 | 返回 model | 包含的方法 |
| --- | --- | --- |
| `sw_industry_index.py` | `SwIndustryIndex` | `get_sw_index_first_info` / `get_sw_index_second_info` / `get_sw_index_third_info` —— 申万一/二/三级行业指数信息，结构相同 |
| `sw_industry_component.py` | `SwIndustryComponent` | `get_sw_index_component` —— 申万行业成分股 |
| `efinance_provider.py` | `pd.DataFrame`（透传） | efinance 专用透传方法 |
| `akshare_ths_provider.py` | TODO | akshare 同花顺数据源相关 |

#### 决策树

新增一个数据获取方法：

```
是否有现成的 provider 文件返回相同 model？
├── 是 → 加到现有文件（如新的"申万二级行业某指标接口"放进 sw_industry_index.py）
└── 否 → 新建一个 provider 文件
        ├── 文件名 = 数据含义（如 sw_industry_component.py）
        ├── 在文件顶部定义 model class（pydantic BaseModel）
        └── 编写 async 方法，返回 List[Model] 或 Model
```

### 3. model 字段统一命名

字段命名严格遵循 [`stock-field-mapping`](../stock-field-mapping/SKILL.md) skill。

**禁止：**
- 自创字段名（如 `stockCode`、`code1`、`name_zh`）
- 同一含义在不同 model 用不同名（如这里叫 `stock_code`，那里叫 `code`）
- 不同含义用同一字段名（如某 model 的 `name` 是股票名，另一个 model 的 `name` 是行业名 → 必须改成 `stock_name` / `industry_name`）

**强制：**
- 股票代码 → `stock_code`
- 股票名称 → `stock_name`
- 板块/行业代码 → `industry_code` / `sector_code` / `sw_industry_code`（按业务前缀区分）
- 板块/行业名称 → `industry_name` / `sector_name` / `sw_industry_name`

### 4. 不同含义字段必须用不同名

避免歧义。常见冲突示例：

| 含义 | 错误命名 | 正确命名 |
| --- | --- | --- |
| 申万行业代码 vs 个股代码 | 都叫 `code` | `sw_industry_code` / `stock_code` |
| 行业名 vs 个股名 | 都叫 `name` | `sw_industry_name` / `stock_name` |
| 行业成分个数 vs 板块成员数 | 都叫 `count` | `sw_component_count` / `member_count` |
| 上级申万行业 vs 上级板块 | 都叫 `parent` | `sw_parent_industry` / `parent_sector` |

新加字段前先全局搜索一次同名字段，确认含义不冲突。

## 标准 provider 文件骨架

```python
from typing import List, Optional
from pydantic import BaseModel
import asyncio
import akshare as ak  # 或 efinance / baostock / etc.


class XxxModel(BaseModel):
    """返回数据的 model，字段命名遵循 stock-field-mapping skill"""
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    # ...其他字段


async def get_xxx(...) -> List[XxxModel]:
    """方法说明，写清楚数据源和字段映射"""
    df = await asyncio.to_thread(ak.xxx_function, ...)
    if df is None or df.empty:
        return []
    return [
        XxxModel(
            stock_code=row["证券代码"],
            stock_name=row["证券名称"],
            # ...
        )
        for _, row in df.iterrows()
    ]
```

要点：

- **同步库调用必须用 `asyncio.to_thread` 包**，避免阻塞事件循环
- model 定义放在文件顶部
- 字段从中文列名映射到英文字段，对照表见 stock-field-mapping skill
- 方法签名 `async def`，返回 `List[Model]` 或 `Model`，不直接返回 DataFrame（透传场景除外）

## 何时拆/合文件

**拆文件**：

- 新接口返回的 model 跟现有所有 provider 文件的 model 都不一样
- 同一文件内 model 字段语义已经超过单一职责（如把"行业指数"和"行业成分股"硬塞一个文件）

**合文件**：

- 新接口返回 model 跟现有文件的 model 完全一致 / 是它的子集 / 强相关（同一种业务对象的不同维度，例如一二三级行业）
- 不要因为"数据源不同"就拆 —— 数据源是实现细节，model 才是组织依据

## 反模式

```python
# 错：直接在 service 里调三方库
# app/service/xxx.py
import akshare as ak
df = ak.stock_zh_a_spot()  # ✗ 必须经过 provider

# 错：一个文件返回多种 model 还混着写
# app/providers/akshare_provider.py（按数据源分文件）
async def get_industry() -> Industry: ...     # ✗
async def get_stock() -> Stock: ...            # ✗ 不同 model 应拆开

# 错：字段名歧义
class Industry(BaseModel):
    code: str  # ✗ 是行业代码？应该叫 sw_industry_code
    name: str  # ✗ 是行业名？应该叫 sw_industry_name
```

## 维护流程

新增 provider 方法时：

1. 看现有 provider 文件，找返回相同 model 的文件 → 加进去
2. 找不到 → 新建文件，文件名描述 model 含义
3. 设计字段时查 stock-field-mapping skill，没有的字段按命名约定补齐并更新对照表
4. 全局搜一遍新字段名，确认没和其它 model 同名异义
5. **同步字段对照表**：将新增的字段名和对应的中文含义追加到 `FastAPI/app/field_map.md` 文件中，保持该文件是项目内所有 model 字段的完整对照表

### 关于 `app/field_map.md`

这是项目内的字段对照总表，每次新增或修改 model 字段后**必须同步更新**。格式示例：

```markdown
| 英文字段 | 中文含义 | 所属 model |
| --- | --- | --- |
| stock_code | 股票代码 | 通用 |
| sw_industry_l1_name | 申万一级行业名称 | SwIndustryThirdCons |
```

维护原则：
- 每次新增 provider 或修改 model 字段后，立即更新此文件
- 按字段分类组织（基础信息、行情、估值、资金流向等）
- 标注字段所属的 model，方便排查同名冲突
- 此文件是唯一权威来源，代码中的字段命名以此为准
