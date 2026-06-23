"""Service 层抽象基类 — 统一接口规范、错误处理。

设计原则：
1. Service 不管缓存（缓存在 provider 层）
2. Service 只做业务逻辑编排
3. 统一返回 Result[T] 封装成功/失败
4. 统一错误处理

使用示例：
    class MyService(BaseService[返回类型]):
        async def _execute(self) -> 返回类型:
            # 业务逻辑：调用 provider、组装数据
            data = await some_provider()
            return transform(data)

    # 调用
    service = MyService(params)
    result = await service.execute()
    if result.success:
        use(result.data)
    else:
        log(result.error)
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    """统一返回格式"""

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: T) -> "Result[T]":
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(cls, error: str) -> "Result[T]":
        return cls(success=False, data=None, error=error)


class BaseService(ABC, Generic[T]):
    """Service 层抽象基类

    子类实现 _execute() 方法（核心业务逻辑）
    调用 execute() 自动处理错误

    注意：缓存在 provider 层，service 不管缓存
    """

    @abstractmethod
    async def _execute(self) -> T:
        """核心业务逻辑，由子类实现。失败时抛异常。"""
        pass

    async def execute(self) -> Result[T]:
        """执行业务逻辑（带错误处理）

        Returns:
            Result[T]: 成功时 data 有值，失败时 error 有值
        """
        try:
            data = await self._execute()
            return Result.ok(data)
        except Exception as e:
            error_msg = f"{self.__class__.__name__}: {type(e).__name__}: {str(e)[:200]}"
            return Result.fail(error_msg)
