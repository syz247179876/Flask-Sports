# -*- coding: utf-8 -*-
# @Time  : 2020/12/2 下午11:36
# @Author : 司云中
# @File : user_urls.py
# @Software: Pycharm
from flask import Blueprint
from flask_restful import Api

from application.api.Client.user.auth_api import LoginApi, RegisterApi
from application.api.Client.user.information_api import InformationApi, FindPasswordApi, HobbyCollectApi
from application.api.Client.user.send_code_api import SendCodeApi
from application.utils.json import output_json

user = Blueprint('auth', __name__, url_prefix='/auth-api')  # 添加_解决命名冲突
# user_apis = swagger.docs(
#     Api(user),
#     apiVersion='0.1',
#     basePath='http://127.0.0.1:5001/',
#     produces=["application/json", "text/html"]
# )
user_apis = Api(user)

user_apis.add_resource(LoginApi, '/login-api', endpoint='login')
user_apis.add_resource(RegisterApi, '/register-api', endpoint='register')
user_apis.add_resource(SendCodeApi, '/code-api', endpoint='code')
user_apis.add_resource(InformationApi, '/information-api', endpoint='information')
user_apis.add_resource(FindPasswordApi, '/password-first-api', endpoint='password')
user_apis.add_resource(HobbyCollectApi, '/hobby-api', endpoint='hobby')

user_apis.representation(mediatype='application/json')(output_json)  # 自定义返回格式
