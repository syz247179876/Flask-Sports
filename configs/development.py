# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:24
# @Author : 司云中
# @File : development.py
# @Software: Pycharm


class DevelopmentConfig(object):
    """the config of development env"""
    MONGODB_DB = ''
    MONGODB_HOST = ''
    MONGODB_PORT = ''
    MONGODB_USERNAME = ''
    MONGODB_PASSWORD = ''

    BUNDLE_ERRORS = True  # 捆绑API中所有参数的错误


development_config = DevelopmentConfig()
