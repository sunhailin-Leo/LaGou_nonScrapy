# -*- coding: UTF-8 -*-
"""
Created on 2018年1月26日
@author: Leo
"""

# Python内置库
import sys

# 项目内部库
from spider.lagou import LagouSpider
from logger.LoggerHandler import Logger
from db.mgo import Mgo

# 日志中心
logger = Logger(logger='starter.py').get_logger()


class Starter:
    def __init__(self, keyword: str, login_username: str, login_password: str):
        # 爬虫配置项
        self._keyword = keyword
        self._login_user = login_username
        self._login_pwd = login_password

        # 爬虫初始化
        self._lagou = LagouSpider(keyword=self._keyword,
                                  login_username=self._login_user,
                                  login_password=self._login_pwd)

        # 初始化数据库连接池
        self.db_connect_pool = []

        # 加载数据库
        # # MongoDB
        self._mgo = Mgo().conn
        self._connect_info(conn_res=self._mgo, db_type="MongoDB")

    def _connect_info(self, conn_res, db_type: str):
        """
        检查数据库连接情况,并写入连接池
        :param conn_res: 连接结果
        :param db_type: 数据库类型名称
        :return: 无返回值
        """
        if conn_res is not None:
            logger.info("%s 数据库连接成功!" % db_type)
            self.db_connect_pool.append(conn_res)
            return True
        else:
            logger.info("%s 数据源没有启用,请检查配置文件或检查数据库连接情况!" % db_type)
            return False

    def start(self, start: int, end=31):
        """
        启动爬虫
        :param start: 页面起始页
        :param end: 页面结束页
        :return:
        """
        if start < 0:
            logger.error("Page num of start is error!")
            sys.exit(1)
        else:
            if start == 0:
                start += 1
            logger.info("起始页: %d; 结束页: %d" % (start, end))
            self._lagou.parse(page_start=start,
                              page_end=end)


if __name__ == '__main__':
    s = Starter(keyword="大数据",
                login_username="",
                login_password="")
    # 测试到222页面 --- 2018.02.08
    s.start(start=0, end=222)
