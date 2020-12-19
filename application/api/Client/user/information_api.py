# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 下午9:02
# @Author : 司云中
# @File : modify.py
# @Software: Pycharm

"""
修改密码API
修改个人信息API
"""
from bson import ObjectId
from flask import current_app, g
from flask_restful import Resource, fields, marshal_with, reqparse
from werkzeug.datastructures import FileStorage
from application.api.Client.user import authenticate_jwt
from application.utils.api_permission import api_permission_check
from application.utils.exception import ModifyInformationError
from application.utils.fields import username_string, phone_string, identify_code_string, ip_string, password_string
from application.utils.success_code import response_code
from extensions.oss import oss
from extensions.redis import manager_redis_operation
from application.utils.exception import CodeError


class InformationApi(Resource):
    method_decorators = [api_permission_check, authenticate_jwt]  # 认证

    folder = 'HeadImage'

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
        return g.user.get_identity()

    def modify_information(self, **kwargs):
        """修改个人信息"""
        identity = self.get_user_phone()
        User = current_app.config.get('user')
        try:
            User.objects(id=ObjectId(identity)).update_one(**kwargs)
            # 发送信号更新session中的user的信息
            # update_session_user_signal.send(self, **kwargs)
        except Exception:
            raise ModifyInformationError()

    @marshal_with(resource_fields)
    def get(self):
        """显示个人信息"""
        user = g.user
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
        user = getattr(g, 'user' ,None)
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('head_image', type=FileStorage, help='文件格式不正确', location='files', required=True)
        args = parser.parse_args()
        outer_net = oss.upload_file(args.get('head_image'), self.folder)
        user.save_head_image_url(file_url=outer_net)
        return response_code.modify_head_image_success


class FindPasswordApi(Resource):
    """
    找回密码

    找回密码(1)：
        1.输入手机号
        2.获取手机号验证码
        3.验证手机号和验证码是否吻合,如果吻合,需要生成修改唯一密码凭证,确保当前手机号/邮箱与之前的手机号/邮箱一致(可以前端传客户端mac)

        (验证通过，无回复内容进入重置密码界面）
    """

    CACHE_NAME = 'code'

    def validate(self):
        """
        校验数据
        :return:dict
        """
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('phone', type=phone_string, help='手机号格式不正确', required=True)
        parser.add_argument('code', type=identify_code_string, help='验证码格式不正确', required=True)
        parser.add_argument('X-FORWARD-FOR', type=ip_string, location='headers', dest='ip')
        return parser.parse_args()

    def save_ident(self, phone, ip):
        """
        记录唯一凭证,用于确保在修改密码和验证码校验分为两个界面情况下,由同一个用户完成
        :param phone: 手机号
        """
        with manager_redis_operation() as manager:
            manager.save_ident(phone, ip, self.CACHE_NAME)

    def post(self):
        args = self.validate()
        phone = args.get('phone')
        with manager_redis_operation() as manager:
            is_correct = manager.check_code(phone, args.get('code'))
            if not is_correct:
                raise CodeError()
            # 记录唯一凭证
            self.save_ident(phone, args.get('ip'))
            return {'status':'go on!'}, 204 # 进入修改密码页



class ModifyPasswordApi(Resource):
    """
    修改密码

    二  针对找回密码后修改密码流程:

    1.比较唯一凭证是否是之前的手机号用户(由redis记录)
    2.修改密码
    3.返回修改结果,删除唯一凭证

    一 针对直接修改密码:

    需要数据:
    1) 旧密码
    2) 新密码
    3) 手机验证码

    校验,修改密码,返回响应
    """

    def validate_retrieve_modify_password(self):
        """
        validate fields regrading with the way of retrieve password
        """

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('new_password', type=password_string, help='密码格式不正确', required=True)
        parser.add_argument('phone', type=phone_string, help='手机号格式不正确', required=True)
        return parser.parse_args()


    def post(self):
        args = self.validate_retrieve_modify_password()




