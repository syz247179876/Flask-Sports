# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:23
# @Author : 司云中
# @File : __init__.py.py
# @Software: Pycharm
from flask import Flask

from application.models import get_user_model, register_all_model
from application.urls.integral_url import integral
from application.urls.manager.integral_manage_url import integral_manager
from application.urls.sport_url import sport
from application.urls.user_urls import user
from application.signals.handle_signal import signal
from extensions.database import db
from extensions.extensions import celery_app, redis_app, sms
from configs import load_config
from flask import got_request_exception

from extensions.oss import oss
from extensions.swaggers import swagger
from log import setup_log

CONFIGS = {
    "1": "TESTING",
    "2": "DEVELOPMENT",
    "3": "PRODUCTION"
}


def log_exception(sender, exception, **extra):
    """ 记录请求的异常"""
    sender.logger.debug('Got exception during processing: %s', exception)



def create_app():
    """create flask-sports app"""

    app = Flask(__name__)

    app.secret_key = '4A8BF09E6732FDC682988A8SYZ666AB7CF53176D08631E'

    config = load_config(CONFIGS['2'])  # 选择环境

    # load logger
    setup_log(config)

    # load config
    app.config.from_object(config)

    # register blueprint
    # Client
    app.register_blueprint(user)
    app.register_blueprint(sport)
    app.register_blueprint(integral)

    # Manager
    app.register_blueprint(integral_manager)


    celery_app.init_app(app)   # 注册celery应用
    redis_app.init_app(app)    # 注册redis应用
    sms.init_app(app)          # 注册阿里云短信服务
    signal.init_app(app)       # 注册发送验证码信号
    db.init_app(app)           # 注册mongodb实例
    swagger.init_app(app)      # 注册Swagger接口文档工具
    oss.init_app(app)          # 注册OSS服务


    with app.app_context():
        get_user_model(app) # 注册用户模型表
        register_all_model(app)   # 注册其余模型表,在应用上下文内通过current_app.config.get('models').get(model_name)进行访问

    got_request_exception.connect(log_exception, app) # 记录请求的异常

    return app
