# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:24
# @Author : 司云中
# @File : development.py
# @Software: Pycharm
import os

from flask import current_app

from configs.default import DefaultConfig


class DevelopmentConfig(DefaultConfig):
    """the config of development env"""

    # 项目路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 密钥!
    SECRET = 'uMfBdlYid2CYfkYkpeB2PCB-NlwFhM-ppd5FC4ToGMQgRE4c_xEFAlFthHjI3N1qU1sUdcBCplaPydp1Zo_xxw'

    # 发行人
    ISSUER = 'syz:247179876'

    # 私钥文件路径
    PRIVATE_PATH = os.path.join(BASE_DIR,'keys/private_key.pem')

    # 公钥文件文件路径

    PUBLIC_PATH = os.path.join(BASE_DIR, 'keys/public_key.pem')

    DEBUG = True
    TESTING = False

    JWT_REFRESH_DAY = 7
    JWT_EXPIRE_DAY = 1

    # 注意url的优先级大于db
    MONGODB_SETTINGS = {
        'db':'flask_sports',
        'host':'mongodb://127.0.0.1:27017/flask_sports'
    }

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
    ACCESS_KEY_ID = ''
    ACCESS_KEY_SECRET = ''
    REGION = 'cn-hangzhou'
    SIGN_NAME = 'ACC商城'  # 短信签名

    # 不同的短信模板
    TEMPLATES_CODE_LOGIN = 'SMS_199795817'
    TEMPLATES_CODE_REGISTER = 'SMS_199795814'
    TEMPLATES_CODE_IDENTIFY = 'SMS_199805896'
    TEMPLATES_CODE_MODIFY_PASSWORD = 'SMS_199805895'
    TEMPLATES_CODE_RETRIEVE_PASSWORD = ''

    # 加密算法
    PASSWORD_HASHERS = [
        'application.utils.crypto.pbkdf2_crypto'
    ]


development_config = DevelopmentConfig()