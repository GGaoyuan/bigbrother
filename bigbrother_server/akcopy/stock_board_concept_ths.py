#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/3/27 14:20
Desc: 同花顺-板块-概念板块
https://q.10jqka.com.cn/thshy/
"""

from typing import Dict
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from bs4 import BeautifulSoup
import py_mini_racer

from akcopy.datasets import get_ths_js
from akcopy.utils import demjson
from akcopy.utils.tqdm import get_tqdm


def _get_file_content_ths(file: str = "ths.js") -> str:
    """
    获取 JS 文件的内容
    :param file:  JS 文件名
    :type file: str
    :return: 文件内容
    :rtype: str
    """
    setting_file_path = get_ths_js(file)
    with open(setting_file_path, encoding="utf-8") as f:
        file_data = f.read()
    return file_data


@lru_cache()
def _get_stock_board_concept_name_ths() -> dict:
    """
    获取同花顺概念板块代码和名称字典
    :return: 获取同花顺概念板块代码和名称字典
    :rtype: dict
    """
    js_code = py_mini_racer.MiniRacer()
    js_content = _get_file_content_ths("ths.js")
    js_code.eval(js_content)
    v_code = js_code.call("v")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/89.0.4389.90 Safari/537.36",
        "Cookie": f"v={v_code}",
    }
    url = "https://q.10jqka.com.cn/gn/detail/code/307822/"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, features="lxml")
    code_list = [
        item["href"].split("/")[-2]
        for item in soup.find(name="div", attrs={"class": "cate_inner"}).find_all("a")
    ]
    name_list = [
        item.text
        for item in soup.find(name="div", attrs={"class": "cate_inner"}).find_all("a")
    ]
    print("aaaaaaaaaaaaaaa")
    name_code_map = dict(zip(name_list, code_list))
    print("bbbbbbbbb")
    temp_dict = __stock_board_concept_summary_ths()
    print("ccccccccc")
    name_code_map.update(temp_dict)
    print("ddddddddddddd")
    return name_code_map


def stock_board_concept_name_ths() -> pd.DataFrame:
    """
    同花顺-板块-概念板块-概念
    http://q.10jqka.com.cn/thshy/
    :return: 所有概念板块的名称和链接
    :rtype: pandas.DataFrame
    """
    code_name_ths_map = _get_stock_board_concept_name_ths()
    temp_df = pd.DataFrame.from_dict(code_name_ths_map, orient="index")
    temp_df.reset_index(inplace=True)
    temp_df.columns = ["name", "code"]
    temp_df = temp_df[
        [
            "name",
            "code",
        ]
    ]
    return temp_df


def _fetch_single_page(headers: dict, page: int) -> Dict:
    """
    获取单个页面的数据（用于并行处理）
    :param headers: 请求头
    :type headers: dict
    :param page: 页码
    :type page: int
    :return: 页面数据字典
    :rtype: dict
    """
    url = f"http://q.10jqka.com.cn/gn/index/field/addtime/order/desc/page/{page}/ajax/1/"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, features="lxml")
        temp_dict = {
            item.get_text(): item["href"].rsplit("/")[-2]
            for item in soup.find_all(name="a")
            if "detail" in item["href"]
        }
        return temp_dict
    except (ValueError, Exception) as e:
        print(f"获取第 {page} 页失败: {e}")
        return {}


@lru_cache()
def __stock_board_concept_summary_ths() -> Dict:
    """
    同花顺-数据中心-概念板块-概念时间表-辅助函数（并行版本）
    https://q.10jqka.com.cn/gn/
    :return: 概念时间表
    :rtype: dict
    """
    js_code = py_mini_racer.MiniRacer()
    js_content = _get_file_content_ths("ths.js")
    js_code.eval(js_content)
    v_code = js_code.call("v")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/89.0.4389.90 Safari/537.36",
        "Cookie": f"v={v_code}",
    }
    url = "http://q.10jqka.com.cn/gn/index/field/addtime/order/desc/page/1/ajax/1/"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, features="lxml")
    page_num = int(soup.find(name="span", attrs={"class": "page_info"}).text.split("/")[1])
    
    big_dict = dict()
    tqdm = get_tqdm()
    print("eeeeeeeeeeeeeee - 开始并行获取数据")
    
    # 使用线程池并行处理多个页面请求
    # max_workers 可以根据实际情况调整，建议设置为 5-10
    max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_page = {
            executor.submit(_fetch_single_page, headers, page): page 
            for page in range(1, page_num + 1)
        }
        
        # 使用 tqdm 显示进度
        for future in tqdm(as_completed(future_to_page), total=page_num, leave=False):
            page = future_to_page[future]
            try:
                temp_dict = future.result()
                if temp_dict:
                    big_dict.update(temp_dict)
            except Exception as e:
                print(f"处理第 {page} 页时出错: {e}")
    
    print(f"并行获取完成，共获取 {len(big_dict)} 条数据")
    return big_dict

