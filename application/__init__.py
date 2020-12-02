# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:23
# @Author : 司云中
# @File : __init__.py.py
# @Software: Pycharm
from flask import Flask


from application.urls.test_urls import test
from configs import load_config

CONFIGS = {
    "1":"TESTING",
    "2":"DEVELOPMENT",
    "3":"PRODUCTION"
}

def create_app():

    """create flask-sports app"""

    app = Flask(__name__)

    app.secret_key = '4A8BF09E6732FDC682988A8SYZ666AB7CF53176D08631E'

    # load config
    # config = load_config(CONFIGS['2'])
    # app.config.from_object(config)

    # register blueprint
    app.register_blueprint(test)
    # app.register_blueprint(bp)  # 导入认证蓝图
    # app.register_blueprint(auth)
    # app.register_blueprint(sport)
    # app.register_blueprint(commodity)
    # app.register_blueprint(error)

    return app