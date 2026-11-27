"""定义股票接口共用的字段约束。"""

from typing import Annotated

from fastapi import Path


Symbol = Annotated[str, Path(pattern=r"^[0-9]{6}$", description="六位 A 股代码")]
MAX_TIMESTAMP = 4_102_444_800
