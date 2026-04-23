from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.response import ApiResponse
from app.dependencies import verify_auth
from app.core.config import settings
from app.providers.akshare import AKShareProvider
from app.bean import MarketSentimentBean

router = APIRouter()

_providers = {
    "akshare": AKShareProvider(),
}


class MarketSentimentRequest(BaseModel):
    date: str  # 格式: YYYY-MM-DD


class GridItem(BaseModel):
    label: str
    value: str
    color: str
    sub: str | None = None


class MarketSentimentResponse(BaseModel):
    score: int
    grid: list[GridItem]


def calculate_sentiment_score(
    up_count: int,
    down_count: int,
    limit_up_count: int,
    limit_down_count: int,
    avg_change_pct: float
) -> int:
    """
    计算市场情绪分数（0~100）

    算法：
    - 基础分 50
    - 涨跌比例影响：±20 分（上涨占比越高得分越高）
    - 涨跌停比例影响：±15 分（涨停占比越高得分越高）
    - 平均涨跌幅影响：±15 分（以 ±3% 为满分边界）
    """
    score = 50.0

    # 涨跌比例（最多 ±20 分）
    total = up_count + down_count
    if total > 0:
        score += (up_count / total - 0.5) * 40

    # 涨跌停比例（最多 ±15 分）
    limit_total = limit_up_count + limit_down_count
    if limit_total > 0:
        score += (limit_up_count / limit_total - 0.5) * 30

    # 平均涨跌幅（最多 ±15 分，以 ±3% 为满分边界）
    score += max(-15, min(15, avg_change_pct * 5))

    return max(0, min(100, round(score)))


def build_response(stats: MarketSentimentBean) -> MarketSentimentResponse:
    """将 MarketSentimentBean 组装成前端所需的响应格式"""
    # 成交额转换为亿元，若有昨日对比则附加百分比变化
    total_volume = round(stats.total_volume / 1e8)
    volume_label = f"{int(total_volume)}亿"
    if stats.volume_vs_yesterday is not None:
        sign = "+" if stats.volume_vs_yesterday >= 0 else ""
        volume_label += f"（{sign}{stats.volume_vs_yesterday}%）"

    score = calculate_sentiment_score(
        stats.up_count, stats.down_count,
        stats.limit_up_count, stats.limit_down_count,
        stats.avg_change_pct,
    )

    return MarketSentimentResponse(
        score=score,
        grid=[
            GridItem(label="上涨", value=str(stats.up_count), color="#e53935"),
            GridItem(label="下跌", value=str(stats.down_count), color="#43a047"),
            GridItem(label="涨跌对比", value=str(stats.up_down_ratio), color="#e53935" if stats.up_count > stats.down_count else "#43a047", sub="涨/跌"),
            GridItem(label="涨停", value=str(stats.limit_up_count), color="#e53935"),
            GridItem(label="跌停", value=str(stats.limit_down_count), color="#43a047"),
            GridItem(label="涨跌停对比", value=str(stats.limit_ratio), color="#e53935" if stats.limit_up_count > stats.limit_down_count else "#43a047", sub="涨停/跌停"),
            GridItem(label="炸板率", value=f"{stats.blow_rate}%", color="#fb8c00"),
            GridItem(label="最高连板", value=f"{stats.max_streak}板", color="#e53935"),
            GridItem(label="成交量", value=volume_label, color="#1565c0"),
        ],
    )


@router.post("/market-sentiment")
async def get_market_sentiment(body: MarketSentimentRequest, _auth=Depends(verify_auth)):
    provider = _providers[settings.datasource]
    try:
        stats = await provider.get_market_sentiment(body.date)
        return ApiResponse.ok(build_response(stats))
    except Exception as e:
        return ApiResponse.error(500, str(e))
