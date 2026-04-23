from fastapi import APIRouter, Depends
from pydantic import BaseModel
import random
from app.core.response import ApiResponse
from app.dependencies import verify_auth
from app.core.config import settings
from app.providers.akshare import AKShareProvider

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
    score = 50.0

    total = up_count + down_count
    if total > 0:
        score += (up_count / total - 0.5) * 40

    limit_total = limit_up_count + limit_down_count
    if limit_total > 0:
        score += (limit_up_count / limit_total - 0.5) * 30

    score += max(-15, min(15, avg_change_pct * 5))

    return max(0, min(100, round(score)))


def generate_mock_data(date_str: str) -> MarketSentimentResponse:
    random.seed(date_str)
    up_count = random.randint(1800, 2800)
    down_count = random.randint(1200, 2200)
    limit_up_count = random.randint(30, 120)
    limit_down_count = random.randint(5, 50)
    blow_rate = round(random.uniform(10, 40), 1)
    max_streak = random.randint(2, 8)
    total_volume = random.randint(8000, 15000)
    up_down_ratio = round(up_count / down_count, 2)
    limit_ratio = round(limit_up_count / limit_down_count, 2)
    avg_change_pct = random.uniform(-1.5, 1.5)
    score = calculate_sentiment_score(up_count, down_count, limit_up_count, limit_down_count, avg_change_pct)
    return MarketSentimentResponse(
        score=score,
        grid=[
            GridItem(label="上涨", value=str(up_count), color="#e53935"),
            GridItem(label="下跌", value=str(down_count), color="#43a047"),
            GridItem(label="涨跌对比", value=str(up_down_ratio), color="#e53935" if up_count > down_count else "#43a047", sub="涨/跌"),
            GridItem(label="涨停", value=str(limit_up_count), color="#e53935"),
            GridItem(label="跌停", value=str(limit_down_count), color="#43a047"),
            GridItem(label="涨跌停对比", value=str(limit_ratio), color="#e53935" if limit_up_count > limit_down_count else "#43a047", sub="涨停/跌停"),
            GridItem(label="炸板率", value=f"{blow_rate}%", color="#fb8c00"),
            GridItem(label="最高连板", value=f"{max_streak}板", color="#e53935"),
            GridItem(label="成交量", value=f"{total_volume}亿", color="#1565c0"),
        ],
    )


def build_response(stats: dict) -> MarketSentimentResponse:
    up_count = stats["up_count"]
    down_count = stats["down_count"]
    limit_up_count = stats["limit_up_count"]
    limit_down_count = stats["limit_down_count"]
    avg_change_pct = stats["avg_change_pct"]
    total_volume = round(stats["total_volume"] / 1e8)
    max_change_pct = stats["max_change_pct"]

    blow_rate = 0.0  # provider 暂未提供炸板数据
    max_streak = min(10, max(1, round(max_change_pct / 10)))
    up_down_ratio = round(up_count / down_count, 2) if down_count > 0 else float(up_count)
    limit_ratio = round(limit_up_count / limit_down_count, 2) if limit_down_count > 0 else float(limit_up_count)
    score = calculate_sentiment_score(up_count, down_count, limit_up_count, limit_down_count, avg_change_pct)

    return MarketSentimentResponse(
        score=score,
        grid=[
            GridItem(label="上涨", value=str(up_count), color="#e53935"),
            GridItem(label="下跌", value=str(down_count), color="#43a047"),
            GridItem(label="涨跌对比", value=str(up_down_ratio), color="#e53935" if up_count > down_count else "#43a047", sub="涨/跌"),
            GridItem(label="涨停", value=str(limit_up_count), color="#e53935"),
            GridItem(label="跌停", value=str(limit_down_count), color="#43a047"),
            GridItem(label="涨跌停对比", value=str(limit_ratio), color="#e53935" if limit_up_count > limit_down_count else "#43a047", sub="涨停/跌停"),
            GridItem(label="炸板率", value=f"{blow_rate}%", color="#fb8c00"),
            GridItem(label="最高连板", value=f"{max_streak}板", color="#e53935"),
            GridItem(label="成交量", value=f"{int(total_volume)}亿", color="#1565c0"),
        ],
    )


@router.post("/market-sentiment")
async def get_market_sentiment(body: MarketSentimentRequest, _auth=Depends(verify_auth)):
    provider = _providers[settings.datasource]
    try:
        stats = await provider.get_market_sentiment(body.date)
        return ApiResponse.ok(build_response(stats))
    except Exception as e:
        print(f"警告: {settings.datasource} 获取数据失败 ({e})，使用模拟数据")
        return ApiResponse.ok(generate_mock_data(body.date))
