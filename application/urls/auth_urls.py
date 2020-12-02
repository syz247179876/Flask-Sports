# -*- coding: utf-8 -*-
# @Time  : 2020/12/2 下午11:36
# @Author : 司云中
# @File : auth_urls.py
# @Software: Pycharm
from flask import Blueprint
from flask_restful import Api

from application.api.auth import RegisterApi
from application.utils.json import output_json

auth = Blueprint('auth', __name__, url_prefix='/user-api')
auth_api = Api(auth)
auth_api.representation(mediatype='application/json')(output_json)  # 自定义返回格式


auth_api.add_resource(LoginApi,'/login',endpoint='login')
auth_api.add_resource(RegisterApi, '/register', endpoint='register')
