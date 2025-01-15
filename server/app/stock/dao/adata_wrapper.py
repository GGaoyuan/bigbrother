from .field_mapper import *
import adata
from pandas import DataFrame


def get_stock_core_concept(stock_code: str) -> DataFrame:
    """
    单只股票所属概念，App中的题材详情的数据
    :param stock_code:股票代码；例：300033
    :return:
    """
    try:
        df = adata.stock.info.get_concept_east(stock_code=stock_code)
        df = df.rename(columns={
            CONCEPT_CODE: CODE
        })
        return df
    except Exception as e:
        print(f"获取概念板块失败: {e}")
        return DataFrame()


def get_stock_industry(stock_code: str) -> DataFrame:
    """
    获取单只股票所属的行业信息
    :param stock_code:股票代码；例：300033
    :return:
    """
    try:
        df = adata.stock.info.get_plate_east(stock_code=stock_code, plate_type=1)
        df = df.rename(columns={
            'plate_code': CODE,
            'plate_name': NAME,
        })
        return df
    except Exception as e:
        print(f"获取行业板块失败: {e}")
        return DataFrame()


def get_stock_district(stock_code: str) -> DataFrame:
    """
    获取单只股票所属的地区信息
    :param stock_code:股票代码；例：300033
    :return:
    """
    try:
        df = adata.stock.info.get_plate_east(stock_code=stock_code, plate_type=2)
        return df
    except Exception as e:
        print(f"获取地域板块失败: {e}")
        return DataFrame()


def get_stock_total_concept(stock_code: str) -> DataFrame:
    """
    获取单只股票所属的概念信息
    :param stock_code:股票代码；例：300033
    :return:
    """
    try:
        df = adata.stock.info.get_plate_east(stock_code=stock_code, plate_type=3)
        return df
    except Exception as e:
        print(f"获取概念板块失败: {e}")
        return DataFrame()

