# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:24
# @Author : 司云中
# @File : development.py
# @Software: Pycharm
from configs.default import DefaultConfig


class DevelopmentConfig(DefaultConfig):
    """the config of development env"""
    DEBUG = True
    TESTING = False

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
        dict(host='0.0.0.0', port=6381, password='', db=10),
        dict(host='0.0.0.0', port=6380, password='', db=10),
        dict(host='0.0.0.0', port=6379, password='', db=10),
    ]

    REDIS_DB_URL = {
        'host': '0.0.0.0',
        'port': 6381,
        'password': '',
        'db': 10
    }

    # 唯一表示redis实例的title
    REDIS_TITLE = 'sports'

    # celery broker
    CELERY_BROKER_URL = 'redis://@127.0.0.1:6381/0'

    # celery backend
    CELERY_RESULT_BACKEND = 'redis://@127.0.0.1:6381/1'

    CELERY_TASK_SERIALIZER = 'json'

    CELERY_RESULT_SERIALIZER = 'json'

    CELERY_TASK_NAME = 'sport-tasks'

    # 阿里云短信参数
    ACCESS_KEY_ID = 'LTAI4GL2hJHQWu5YRUoVhSw8'
    ACCESS_KEY_SECRET = 'OCy6Lxu5QFrCrWDQvOr3TIZPV6AsqA'
    REGION = 'cn-hangzhou'
    SIGN_NAME = 'ACC商城'  # 短信签名

    # 不同的短信模板
    TEMPLATES_CODE_LOGIN = 'SMS_199795817'
    TEMPLATES_CODE_REGISTER = 'SMS_199795814'
    TEMPLATES_CODE_IDENTIFY = 'SMS_199805896'
    TEMPLATES_CODE_MODIFY_PASSWORD = 'SMS_199805895'
    TEMPLATES_CODE_RETRIEVE_PASSWORD = ''


development_config = DevelopmentConfig()
