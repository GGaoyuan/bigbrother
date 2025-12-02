#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
工具模块
"""

from akcopy.utils import demjson as demjson_module
from akcopy.utils.tqdm import get_tqdm

# 为了兼容性，导出 demjson
demjson = demjson_module

__all__ = ['demjson', 'get_tqdm']

