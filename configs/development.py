# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:24
# @Author : 司云中
# @File : development.py
# @Software: Pycharm
import logging
import os

from celery.schedules import crontab

from configs.default import DefaultConfig


class DevelopmentConfig(DefaultConfig):
    """the config of development env"""

    # 项目路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 密钥!
    SECRET = 'uMfBdlYid2CYfkYkpeB2PCB-NlwFhM-ppd5FC4ToGMQgRE4c_xEFAlFthHjI3N1qU1sUdcBCplaPydp1Zo_xxw'

    # 日志等级
    LOG_LEVEL = logging.ERROR

    # 发行人
    ISSUER = 'syz:247179876'

    # 私钥文件路径
    PRIVATE_PATH = os.path.join(BASE_DIR, 'keys/private_key.pem')

    # 公钥文件文件路径

    PUBLIC_PATH = os.path.join(BASE_DIR, 'keys/public_key.pem')

    DEBUG = True
    TESTING = False

    JWT_REFRESH_DAY = 7
    JWT_EXPIRE_DAY = 1

    # 注意url的优先级大于db
    MONGODB_SETTINGS = {
        'db': 'flask_sports',
        'host': 'mongodb://127.0.0.1:27017/flask_sports'
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

    REDIS_DB = {
        'default':
            {
                'host': '0.0.0.0',
                'port': 6381,
                'password': '',
                'db': 1
            },
        'whole':
            {
                'host': '0.0.0.0',
                'port': 6381,
                'password': '',
                'db': 2
            },
        'user':
            {
                'host': '0.0.0.0',
                'port': 6381,
                'password': '',
                'db': 3
            },
        'code':
            {
                'host': '0.0.0.0',
                'port': 6381,
                'password': '',
                'db': 4
            },
        'rate':
            {
                'host': '0.0.0.0',
                'port': 6381,
                'password': '',
                'db': 5
            },
        'redis5':
            {
                'host': '0.0.0.0',
                'port': 6381,
                'password': '',
                'db': 6
            }
    }

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

    CELERY_TASKS_FUNC = [
        'application.tasks.sport_task.timer_rewrite_step_number',
        'application.tasks.user_task.send_phone',
    ]

    # 异步任务
    CELERY_BEAT_SCHEDULE = {
        'rewrite_step_counter': {
            'task': 'application.tasks.sport_task.timer_rewrite_step_number',
            'args': ('step',),
            'schedule': crontab(minute=1, hour=0),
        }
    }

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

    # OSS对象存储

    OSS_ENDPOINT = 'http://oss-cn-beijing.aliyuncs.com'

    OSS_BUCKET_NAME = 'flask-sports'

    OSS_BASE_URL = 'https://flask-sports.oss-cn-beijing.aliyuncs.com/'

    # 加密算法
    PASSWORD_HASHERS = [
        'application.utils.crypto.pbkdf2_crypto'
    ]

    # 认证模型类
    AUTH_USER_MODEL = 'application.models.user_model.User'

    # 模型模块
    APPLICATION_MODELS_MODULE = [
        'application.models.user_model.Address',
        'application.models.sport_model.StepSport',
        'application.models.integral_model.Commodity',
    ]

    SWAGGER = {
        'title': '健康运动APP Api',
        'description': '基于Flask后端的 健康运动APP OpenApi接口',
        'host': '0.0.0.0' # 请求域名
    }

    DEFAULT_THROTTLE_CLASSES = [
        'application.utils.throttle.WholeApiRate',
    ]

    DEFAULT_THROTTLE_RATE = {
        'whole-api':'100/day'
    }



development_config = DevelopmentConfig()
