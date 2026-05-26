import akshare as ak
import efinance as ef
import adata



if __name__ == '__main__':


    # akshare 同花顺行业板块（不走东方财富，避免被限流）
    # df = ak.stock_board_industry_summary_ths()
    # print("行业板块（同花顺）：\n", df)

    # akshare 新浪全市场实时行情（个股）
    # df = ak.stock_zh_a_spot()
    # print("个股实时行情（新浪）：\n", df.head())

    # df = ef.stock.get_realtime_quotes(['行业板块', '概念板块'])
    # ef 调用东方财富接口（容易被限流）
    # df = ef.stock.get_realtime_quotes(['创业板', '港股'])

    # df = ef.stock.get_realtime_quotes()

    # 获取沪深A股最新行情指标
    # 获取概念板块最新行情指标
    # df = qs.get_data('601318')
    # df.tail()

    # stock_board_concept_name_em_df = ak.stock_board_concept_name_em()
    # print(stock_board_concept_name_em_df)

    # df = ef.stock.get_realtime_quotes(['概念板块'])

    # stock_hot_rank_em_df = ak.stock_hot_rank_em()
    # print(stock_hot_rank_em_df)

    # stock_board_industry_name_em_df = ak.stock_board_industry_name_em()
    # print(stock_board_industry_name_em_df)

    # stock_board_industry_spot_em_df = ak.stock_board_industry_spot_em(symbol="小金属")
    # print(stock_board_industry_spot_em_df)
    # print("行情：\n", df)

    # stock_board_industry_summary_ths_df = ak.stock_board_industry_summary_ths()
    # print(stock_board_industry_summary_ths_df)

    df = ak.stock_board_concept_name_ths()
    print(df)

    df2 = ak.stock_board_industry_name_ths()
    print(df2)
    # stock_industry_sina_df = ak.stock_sector_spot(indicator="概念")
    # print(stock_industry_sina_df)
    #
    # stock_industry_sina_df2 = ak.stock_sector_spot(indicator="行业")
    # print(stock_industry_sina_df2)