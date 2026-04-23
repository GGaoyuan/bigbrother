from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

    @classmethod
    def ok(cls, data: Any = None, message: str = "success") -> "ApiResponse":
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str) -> "ApiResponse":
        return cls(code=code, message=message, data=None)
