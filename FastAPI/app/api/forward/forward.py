from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.core.response import ApiResponse
from app.dependencies import verify_auth
import efinance as ef
import akshare as ak
import pandas as pd

router = APIRouter()


class ForwardRequest(BaseModel):
    source: str
    fn: str
    param: Optional[dict] = None


@router.post("/forward")
async def forward_request(body: ForwardRequest, _auth=Depends(verify_auth)):
    try:
        if body.source == "ak":
            module = ak
        elif body.source == "ef":
            module = ef
        else:
            return ApiResponse.error(400, f"不支持的 source: {body.source}")

        fn = getattr(module, body.fn, None)
        if fn is None:
            return ApiResponse.error(400, f"{body.source}.{body.fn} 不存在")

        result = fn(**(body.param or {}))

        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")

        return ApiResponse.ok(result)
    except Exception as e:
        return ApiResponse.error(500, str(e))
