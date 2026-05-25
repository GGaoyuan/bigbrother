import adata as ad
import efinance as ef

if __name__ == '__main__':
    # df = ad.stock.market.get_capital_flow_min(stock_code='BK0457')

    # 1. 获取当前所有 行业板块 的资金流向
    industry_funding = ef.stock.get_industry_funding_ranking()
    print("行业板块资金流向：\n", industry_funding.head())

    # 2. 获取当前所有 概念板块 的资金流向
    concept_funding = ef.stock.get_concept_funding_ranking()
    print("概念板块资金流向：\n", concept_funding.head())

    # 3. 获取某个特定板块（如“半导体”）的历史资金流向
    history_funding = ef.stock.get_history_industry_funding('半导体')
    print("半导体板块历史资金流向：\n", history_funding.head())
    print(df)
