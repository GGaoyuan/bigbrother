import asyncio
import efinance as ef
from typing import List
from app.bean import TodayBillBean, MarketSentimentBean, DailyBarBean, RealtimeQuoteBean
from app.providers.ef import EFProvider
from app.providers.ak import AKProvider

# 默认使用 efinance，akshare 作为备用
_ef = EFProvider()
_ak = AKProvider()


async def get_realtime_sectors(type: int):
    # 1：行业，2：概念，3：全部

    pass

