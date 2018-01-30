# -*- coding: UTF-8 -*-
"""
Created on 2018年1月29日
@author: Leo
"""

import json
import time
from pymongo import MongoClient

# 项目内部库
from logger.LoggerHandler import Logger

# 日志中心
logger = Logger(logger='mgo.py').get_logger()


# DB配置文件路径
DB_CONFIG_PATH = "./conf/db.json"


class Mgo:
    """
    返回MongoDB的对象
    """
    def __init__(self):
        # 加载配置文件
        self._config = self._load_conf()

        # 加载数据库配置
        if self._config is not None and self._config['Enable'] is not False:
            self.conn = self._connect()
        else:
            self.conn = None

    @staticmethod
    def _load_conf() -> dict:
        """
        加载配置文件
        :return:
        """
        try:
            config = json.loads(open(DB_CONFIG_PATH, encoding="UTF-8").read())['MongoDB']
            return config
        except FileNotFoundError:
            config = json.loads(open("." + DB_CONFIG_PATH, encoding="UTF-8").read())['MongoDB']
            return config
        except Exception as err:
            logger.debug("数据库配置文件不存在或无法读取; 错误原因: %s" % str(err))

    def _connect(self) -> MongoClient:
        """
        连接MongoDB数据库
        :return:
        """
        # 判断下用户密码是否存在
        if self._config['Username'] == "" and self._config['Password'] == "":
            conn = MongoClient(host=self._config['Host'],
                               port=self._config['Port'])[self._config['Database']]
        else:
            conn = MongoClient(host=self._config['Host'],
                               port=self._config['Port'],
                               username=self._config['Username'],
                               password=self._config['Password'])[self._config['Database']]

        if conn is not None:
            logger.info("MongoDB连接成功! 配置如下:")
            logger.info("Host: %s, Port:%d, Username: %s, Password: %s"
                        % (self._config['Host'],
                           self._config['Port'],
                           self._config['Username'],
                           self._config['Password']))
            return conn
        else:
            logger.debug("MongoDB数据库连接失败,10s后重试!")
            time.sleep(10)
            self._connect()
