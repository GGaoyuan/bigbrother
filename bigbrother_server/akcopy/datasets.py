# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
Date: 2024/12/30 15:30
Desc: 导入文件工具，可以正确处理路径问题
"""

import pathlib
import os


def get_ths_js(file: str = "ths.js") -> pathlib.Path:
    """
    get path to data "ths.js" text file.
    :return: 文件路径
    :rtype: pathlib.Path
    """
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent
    # 构建数据文件路径
    data_file_path = current_dir / "data" / file
    return data_file_path

