import asyncio
from app.service.industry import get_sw_industry, get_sw_stock_industry
import efinance as ef
import akshare as ak
import adata as ad

if __name__ == '__main__':
    # result = asyncio.run(get_sw_industry())
    # print(result)
    # result2 = asyncio.run(get_sw_stock_industry())
    # print(result2)


    # 有问题
    # df = ef.stock.get_realtime_quotes(['沪深A股'])
    # print(df)
    # stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    # print(stock_zh_a_spot_em_df)

    # stock_zh_index_spot_sina_df = ak.stock_zh_index_spot_sina()
    # print(stock_zh_index_spot_sina_df)


    # 好用
    # df = ad.sentiment.hot.list_a_list_daily(report_date='2026-06-10')
    # print(df)

    # Test
    df = ad.sentiment.hot.pop_rank_100_east()
    print(df)