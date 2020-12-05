# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 下午9:02
# @Author : 司云中
# @File : modify.py
# @Software: Pycharm

"""
修改密码API
修改个人信息API
"""

from flask import session
from flask_restful import Resource, fields, marshal_with, reqparse

from application.api.auth import authenticate
from application.models.user_model import User
from application.signals.signal import update_session_user_signal
from application.utils.exception import ModifyInformationError
from application.utils.fields import username_string
from application.utils.success_code import response_code


class InformationApi(Resource):
    method_decorators = [authenticate] # 认证

    # 过滤字段
    resource_fields = {
        'username': fields.String,
        'integral': fields.Integer,
        'is_active': fields.Boolean(attribute='is_active'),  # 指向数据对象中真正的值,换名
        'phone': fields.String,
        'head_image': fields.String(default='https://flask-sports.oss-cn-beijing.aliyuncs.com/1579793244834816.jpg'),
    }

    def get_user_phone(self):
        """
        获取用户对象的唯一标识
        目前是session方法
        """
        return session.get('user').get('phone')

    def modify_information(self, **kwargs):
        """修改个人信息"""
        identity = self.get_user_phone()
        try:
            User.objects(phone=identity).update_one(**kwargs)
            # 发送信号更新session中的user的信息
            update_session_user_signal.send(self, **kwargs)
        except Exception:
            raise ModifyInformationError()

    @marshal_with(resource_fields)
    def get(self):
        """显示个人信息"""
        user = session.get('user').copy()
        return user

    def post(self):
        """修改用户名"""
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('username', type=username_string, required=True, help='用户名格式不正确')
        args = parser.parse_args()
        self.modify_information(**args)
        return response_code.modify_information_success

    def put(self):
        """修改头像"""
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('head_image', type)