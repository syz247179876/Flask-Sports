# -*- coding: utf-8 -*-
# @Time  : 2020/12/2 下午11:41
# @Author : 司云中
# @File : auth.py
# @Software: Pycharm
from flask_restful import Resource, fields, reqparse


class RegisterApi(Resource):
    """注册Api"""

    def post(self):
        parser = reqparse.RequestParser() # 定义请求解析器,捆绑所有错误统一返回给前端
        parser.add_argument('phone', type=str, required=True, help='手机号格式不正确')
        parser.add_argument('password', type=str, required=True, help='密码格式不规范')
        parser.add_argument('code', type=str, required=True, help='验证码格式不规范')


        pass


class LoginApi(Resource):
    """登录Api"""

    def post(self):
        pass

