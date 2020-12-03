# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:24
# @Author : 司云中
# @File : production.py
# @Software: Pycharm
from configs.default import DefaultConfig


class ProductionConfig(DefaultConfig):
    """the config of production env"""
    DEBUG = False
    TESTING = False
    MONGODB_DB = ''
    MONGODB_HOST = ''
    MONGODB_PORT = ''
    MONGODB_USERNAME = ''
    MONGODB_PASSWORD = ''


production_config = ProductionConfig()
