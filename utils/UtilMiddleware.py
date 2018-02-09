# -*- coding: UTF-8 -*-
"""
Created on 2018年2月8日
@author: Leo
"""
# Python内置库
import re
import time


def filter_html_tag(content: str) -> str:
    """
    过滤文字中的HTML标签
    :param content:
    :return:
    """
    pattern = re.compile(r'<[^>]+>', re.S)
    return pattern.sub('', content)


def get_value(data) -> str:
    """
    :param data: 数据
    :return: 拆分列表后的数据
    """
    info = ''.join(data)
    return info


def time_to_timestamp(time_str: str):
    """
    年月日时分秒转时间戳
    :param time_str: 年月日时分秒
    :return: 时间戳
    """
    return time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S')) * 1000
