# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:23
# @Author : 司云中
# @File : __init__.py.py
# @Software: Pycharm
from flask import Flask


from application.urls.auth_urls import auth_
from application.urls.test_urls import test
from application.utils.extensions import celery_app, redis_app, code_signal, sms, db, encryption
from configs import load_config

CONFIGS = {
    "1": "TESTING",
    "2": "DEVELOPMENT",
    "3": "PRODUCTION"
}

config = load_config(CONFIGS['2'])


def create_app():
    """create flask-sports app"""

    app = Flask(__name__)

    app.secret_key = '4A8BF09E6732FDC682988A8SYZ666AB7CF53176D08631E'

    # load config

    app.config.from_object(config)
    # register blueprint
    # app.register_blueprint(test)
    app.register_blueprint(auth_)

    celery_app.init_app(app)   # 注册celery应用
    redis_app.init_app(app)    # 注册redis应用
    sms.init_app(app)          # 注册阿里云短信服务
    code_signal.init_app(app)  # 注册发送验证码信号
    db.init_app(app)           # 注册mongodb实例

    # app.register_blueprint(bp)  # 导入认证蓝图
    # app.register_blueprint(auth)
    # app.register_blueprint(sport)
    # app.register_blueprint(commodity)
    # app.register_blueprint(error)

    return app
