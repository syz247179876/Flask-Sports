# -*- coding: utf-8 -*-
# @Time  : 2020/12/2 下午11:36
# @Author : 司云中
# @File : auth_urls.py
# @Software: Pycharm
from flask import Blueprint
from flask_restful import Api

from application.api.auth_api import LoginApi, RegisterApi
from application.api.send_code_api import SendCodeApi
from application.utils.json import output_json


auth_ = Blueprint('auth', __name__, url_prefix='/auth-api') # 添加_解决命名冲突


auth_apis = Api(auth_)
auth_apis.add_resource(LoginApi,'/login',endpoint='login')
auth_apis.add_resource(RegisterApi, '/register', endpoint='register')
auth_apis.add_resource(SendCodeApi, '/verification', endpoint='verification')


auth_apis.representation(mediatype='application/json')(output_json)  # 自定义返回格式