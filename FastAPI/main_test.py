import adata as ad
import efinance as ef

if __name__ == '__main__':
    df = ad.stock.info.all_concept_code_east()
    print("行业板块资金流向：\n", df.head())

    # 1. 获取当前所有 行业板块 的资金流向
    # industry_funding = ef.stock.get_today_bill(stock_code='BK0457')
    # print("行业板块资金流向：\n", industry_funding.head())


    # df = ef.stock.get_realtime_quotes(['行业板块', '概念板块'])
    # print("行业板块资金流向：\n", df)

    # df2 = ef.stock.get_realtime_quotes(['概念板块'])
    # print("行业板块资金流向：\n", df2)