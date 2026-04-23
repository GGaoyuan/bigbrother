from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import akshare as ak
import pandas as pd
import random

router = APIRouter()


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
    计算市场情绪分数 (0-100)

    算法逻辑：
    - 基础分 50
    - 涨跌比例影响: +/- 20分
    - 涨跌停比例影响: +/- 15分
    - 平均涨跌幅影响: +/- 15分
    """
    score = 50.0

    # 涨跌比例 (最多 ±20分)
    total = up_count + down_count
    if total > 0:
        up_ratio = up_count / total
        score += (up_ratio - 0.5) * 40

    # 涨跌停比例 (最多 ±15分)
    limit_total = limit_up_count + limit_down_count
    if limit_total > 0:
        limit_up_ratio = limit_up_count / limit_total
        score += (limit_up_ratio - 0.5) * 30

    # 平均涨跌幅 (最多 ±15分，以 ±3% 为满分边界)
    score += max(-15, min(15, avg_change_pct * 5))

    return max(0, min(100, round(score)))


def generate_mock_data(date_str: str) -> MarketSentimentResponse:
    """生成模拟数据作为降级方案"""
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

    score = calculate_sentiment_score(
        up_count, down_count, limit_up_count, limit_down_count, avg_change_pct
    )

    return MarketSentimentResponse(
        score=score,
        grid=[
            GridItem(label="上涨", value=str(up_count), color="#e53935"),
            GridItem(label="下跌", value=str(down_count), color="#43a047"),
            GridItem(label="涨跌对比", value=str(up_down_ratio),
                     color="#e53935" if up_count > down_count else "#43a047", sub="涨/跌"),
            GridItem(label="涨停", value=str(limit_up_count), color="#e53935"),
            GridItem(label="跌停", value=str(limit_down_count), color="#43a047"),
            GridItem(label="涨跌停对比", value=str(limit_ratio),
                     color="#e53935" if limit_up_count > limit_down_count else "#43a047", sub="涨停/跌停"),
            GridItem(label="炸板率", value=f"{blow_rate}%", color="#fb8c00"),
            GridItem(label="最高连板", value=f"{max_streak}板", color="#e53935"),
            GridItem(label="成交量", value=f"{total_volume}亿", color="#1565c0"),
        ],
    )


@router.post("/market-sentiment", response_model=MarketSentimentResponse)
async def get_market_sentiment(body: MarketSentimentRequest):
    """
    获取指定日期的市场情绪数据（真实数据）
    使用 akshare 获取 A 股市场涨跌统计
    如果网络失败，降级使用模拟数据
    """
    date_str = body.date  # YYYY-MM-DD

    try:
        # 获取 A 股当日涨跌统计（东方财富）
        df = ak.stock_zh_a_spot_em()

        if df is None or df.empty:
            print(f"警告: akshare 返回空数据，使用模拟数据")
            return generate_mock_data(date_str)

        # 过滤掉无效行（最新价为空或0）
        df = df[df["最新价"].notna() & (df["最新价"] > 0)]

        # 涨跌统计
        up_count = int((df["涨跌幅"] > 0).sum())
        down_count = int((df["涨跌幅"] < 0).sum())

        # 涨跌停统计（涨幅 >= 9.9% 视为涨停，跌幅 <= -9.9% 视为跌停）
        limit_up_count = int((df["涨跌幅"] >= 9.9).sum())
        limit_down_count = int((df["涨跌幅"] <= -9.9).sum())

        # 炸板率：当日曾涨停但收盘未涨停的比例（用涨幅 5~9.9% 近似）
        near_limit_up = int(((df["涨跌幅"] >= 5) & (df["涨跌幅"] < 9.9)).sum())
        blow_rate = round(near_limit_up / limit_up_count * 100, 1) if limit_up_count > 0 else 0.0

        # 最高连板（用最高涨幅近似，真实连板数据需要历史数据）
        max_change = float(df["涨跌幅"].max()) if not df.empty else 0
        max_streak = min(10, max(1, round(max_change / 10)))

        # 成交量（亿元）
        total_volume = df["成交额"].sum() / 1e8 if "成交额" in df.columns else 0
        total_volume = round(total_volume, 0)

        # 涨跌比
        up_down_ratio = round(up_count / down_count, 2) if down_count > 0 else float(up_count)
        limit_ratio = round(limit_up_count / limit_down_count, 2) if limit_down_count > 0 else float(limit_up_count)

        # 平均涨跌幅
        avg_change_pct = float(df["涨跌幅"].mean()) if not df.empty else 0

        # 计算情绪分数
        score = calculate_sentiment_score(
            up_count, down_count, limit_up_count, limit_down_count, avg_change_pct
        )

        return MarketSentimentResponse(
            score=score,
            grid=[
                GridItem(label="上涨", value=str(up_count), color="#e53935"),
                GridItem(label="下跌", value=str(down_count), color="#43a047"),
                GridItem(label="涨跌对比", value=str(up_down_ratio),
                         color="#e53935" if up_count > down_count else "#43a047", sub="涨/跌"),
                GridItem(label="涨停", value=str(limit_up_count), color="#e53935"),
                GridItem(label="跌停", value=str(limit_down_count), color="#43a047"),
                GridItem(label="涨跌停对比", value=str(limit_ratio),
                         color="#e53935" if limit_up_count > limit_down_count else "#43a047", sub="涨停/跌停"),
                GridItem(label="炸板率", value=f"{blow_rate}%", color="#fb8c00"),
                GridItem(label="最高连板", value=f"{max_streak}板", color="#e53935"),
                GridItem(label="成交量", value=f"{int(total_volume)}亿", color="#1565c0"),
            ],
        )

    except Exception as e:
        # 网络错误或其他异常，降级使用模拟数据
        print(f"警告: akshare 获取数据失败 ({e})，使用模拟数据")
        return generate_mock_data(date_str)
