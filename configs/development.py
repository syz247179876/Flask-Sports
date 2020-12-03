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

    # 捆绑API中所有参数的错误
    BUNDLE_ERRORS = True

    CACHE_NAME = 'redis'

    # redis集群
    STARTUP_NODES = [
        dict(host='0.0.0.0', port=6379, password='', db=10),
        dict(host='0.0.0.0', port=6380, password='', db=10),
        dict(host='0.0.0.0', port=6381, password='', db=10),
    ]

    # 唯一表示redis实例的title
    REDIS_TITLE = 'sports'

    # celery broker
    CELERY_BROKER_URL = 'redis://@127.0.0.1:6382/0'

    # celery backend
    CELERY_RESULT_BACKEND = 'redis://@127.0.0.1:6382/1'

    CELERY_TASK_SERIALIZER = 'json'

    CELERY_RESULT_SERIALIZER = 'json'

    CELERY_TASK_NAME = 'sport-tasks'



development_config = DevelopmentConfig()
