# -*- coding: utf-8 -*-
# @Time  : 2020/12/2 下午11:36
# @Author : 司云中
# @File : auth_urls.py
# @Software: Pycharm
from flask import Blueprint
from flask_restful import Api

from application.api.auth.auth_api import LoginApi, RegisterApi
from application.api.auth.information_api import InformationApi
from application.api.auth.send_code_api import SendCodeApi
from application.utils.json import output_json


auth_ = Blueprint('auth', __name__, url_prefix='/auth-api') # 添加_解决命名冲突


auth_apis = Api(auth_)

auth_apis.add_resource(LoginApi,'/login-api',endpoint='login')
auth_apis.add_resource(RegisterApi, '/register-api', endpoint='register')
auth_apis.add_resource(SendCodeApi, '/code-api', endpoint='code')
auth_apis.add_resource(InformationApi, '/information-api', endpoint='information')

auth_apis.representation(mediatype='application/json')(output_json)  # 自定义返回格式