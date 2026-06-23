"""Provider 层抽象基类 — 统一数据源接口规范。

设计原则：
1. Provider 负责缓存（用 @cached_json 装饰器）
2. Provider 直接对接外部数据源（akshare/efinance/mootdx）
3. Provider 返回统一格式（Pydantic Model 或 dict）
4. Provider 处理数据源特有的异常和重试

使用示例：
    class MyProvider(BaseProvider[返回类型]):
        def __init__(self, param1, param2):
            self.param1 = param1
            self.param2 = param2

        async def _fetch(self) -> 返回类型:
            # 数据源调用逻辑
            df = await asyncio.to_thread(akshare.some_api, self.param1)
            return parse(df)

        @cached_json(key="my_provider_{param1}_{param2}", ttl=CacheTTL.HOURLY)
        async def get(self) -> 返回类型:
            return await self._fetch()

    # 调用
    provider = MyProvider("A", "B")
    data = await provider.get()  # 自动缓存
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseProvider(ABC, Generic[T]):
    """Provider 层抽象基类

    子类实现：
    - _fetch(): 核心数据获取逻辑（对接外部数据源）
    - get(): 对外接口，用 @cached_json 装饰器自动缓存

    注意：
    - _fetch() 不带缓存，纯数据获取
    - get() 带缓存装饰器，对外暴露
    - 失败时抛异常，由上层 service 处理
    """

    @abstractmethod
    async def _fetch(self) -> T:
        """核心数据获取逻辑，由子类实现。

        对接 akshare/efinance/mootdx 等数据源。
        失败时抛异常（不捕获，由 service 层处理）。
        """
        pass

    @abstractmethod
    async def get(self) -> T:
        """对外接口，子类用 @cached_json 装饰此方法。

        Example:
            @cached_json(key="provider_key", ttl=CacheTTL.HOURLY)
            async def get(self) -> T:
                return await self._fetch()
        """
        pass
