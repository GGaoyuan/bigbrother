import akshare as ak
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_limit_up_df(date_str: str) -> pd.DataFrame:
    """
    东方财富网-行情中心-涨停板行情-涨停股池
    """
    stock_zt_pool_em_df = ak.stock_zt_pool_em(date=date_str)
    return stock_zt_pool_em_df


def get_limit_down_df(date_str: str) -> pd.DataFrame:
    """
    东方财富网-行情中心-涨停板行情-跌停股池
    """
    stock_zt_pool_dtgc_em_df = ak.stock_zt_pool_dtgc_em(date=date_str)
    return stock_zt_pool_dtgc_em_df



def get_strong_performing_df(date_str: str) -> pd.DataFrame:
    """
    东方财富网-行情中心-涨停板行情-强势股池
    """
    stock_zt_pool_strong_em_df = ak.stock_zt_pool_strong_em(date=date_str)
    return stock_zt_pool_strong_em_df


def get_industry_board_df() -> pd.DataFrame:
    """
    东方财富网-行情中心-沪深京板块-行业板块
    :return:单次返回当前时刻所有行业板块数据
    """
    try:
        stock_board_industry_name_em_df = ak.stock_board_industry_name_em()
        return stock_board_industry_name_em_df
    except Exception as e:
        print(f"获取行业板块失败: {e}")
        return pd.DataFrame()

def get_industry_board_component_df(name: str) -> pd.DataFrame:
    """
    东方财富-沪深板块-行业板块-板块成份
    :return:单次返回指定 symbol 的所有成份股
    """
    try:
        stock_board_industry_cons_em_df = ak.stock_board_industry_cons_em(symbol=name)
        return stock_board_industry_cons_em_df
    except Exception as e:
        print(f"获取行业板块成分股失败: {e}")
        return pd.DataFrame()


def get_industry_board_components_detail_df() -> pd.DataFrame:
    """
    获取所有的行业板块成分股
    """
    industry_boards = get_industry_board_df()
    if industry_boards.empty:
        print(f"获取行业板块失败")
        return pd.DataFrame()
    # 获取板块名称列表
    industry_names = industry_boards["板块名称"].tolist()
    results = []
    with ThreadPoolExecutor(max_workers=len(industry_names)) as executor:
        futures = {executor.submit(get_industry_board_component_df, board): board for board in industry_names}
        for future in as_completed(futures):
            try:
                result = future.result()
                result['板块名称'] = futures[future]
                results.append(result)
            except Exception as e:
                print(f"线程执行错误: {e}")
    return pd.concat(results, ignore_index=True)

def get_concept_board_df() -> pd.DataFrame:
    """
    东方财富网-行情中心-沪深京板块-概念板块
    :return:单次返回当前时刻所有概念板块数据
    """
    try:
        stock_board_concept_name_em_df = ak.stock_board_concept_name_em()
        return stock_board_concept_name_em_df
    except Exception as e:
        print(f"获取概念板块失败: {e}")
        return pd.DataFrame()


def get_concept_board_component_df(name: str) -> pd.DataFrame:
    """
    东方财富-沪深板块-概念板块-板块成份
    :return:单次返回当前时刻所有成份股
    """
    try:
        stock_board_concept_cons_em_df = ak.stock_board_concept_cons_em(symbol=name)
        return stock_board_concept_cons_em_df
    except Exception as e:
        print(f"获取概念板块成分股失败: {e}")
        return pd.DataFrame()


def get_concept_board_components_detail_df() -> pd.DataFrame:
    """
    获取所有的概念板块成分股
    """
    concept_boards = get_concept_board_df()
    if concept_boards.empty or concept_boards.empty:
        print("获取概念板块名称失败。")
        return pd.DataFrame()
    # 获取板块名称列表
    concept_names = concept_boards["板块名称"].tolist()
    results = []
    with ThreadPoolExecutor(max_workers=len(concept_names)) as executor:
        futures = {executor.submit(get_concept_board_component_df, board): board for board in concept_names}
        for future in as_completed(futures):
            try:
                result = future.result()
                result['板块名称'] = futures[future]
                results.append(result)
            except Exception as e:
                print(f"线程执行错误: {e}")
    return pd.concat(results, ignore_index=True)