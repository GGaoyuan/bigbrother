from fastapi import APIRouter, Depends

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service.analysis import get_market_analysis_dashboard
from app.service.bean import sanitize_json
from app.service.news import get_news_overview

router = APIRouter(tags=["analysis"])


@router.post("/news/overview")
async def get_news_overview(_auth=Depends(verify_auth)):
    """消息面：新闻/宏观/海外指数/问财热点"""
    try:
        data = sanitize_json(await get_news_overview())
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/analysis/dashboard")
async def get_analysis_dashboard(_auth=Depends(verify_auth)):
    """A股市场分析全量数据面板（spec 汇总）"""
    try:
        data = await get_market_analysis_dashboard()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
