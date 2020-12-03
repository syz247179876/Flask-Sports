# -*- coding: utf-8 -*-
# @Time  : 2020/12/2 下午11:41
# @Author : 司云中
# @File : auth-api.py
# @Software: Pycharm
from flask_restful import Resource, fields, reqparse

from application.utils.exception import VerificationCodeException
from application.utils.fields import IdentifyingCodeString, PasswordString, PhoneString, phone_string, password_string, \
    identify_code_string
from application.utils.redis import manager_redis

class RegisterApi(Resource):
    """注册Api"""

    def create_user(self, **kwargs):
        """创建用户"""
        pass


    def validate_code(self, phone, code):
        """验证校验码"""
        with manager_redis() as redis:
            redis_code = redis.get(phone)
            if redis_code != code:
                return False
            return True

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True) # 定义请求解析器,捆绑所有错误统一返回给前端
        parser.add_argument('phone', type=phone_string, required=True, help='手机号格式不正确')
        parser.add_argument('password', type=password_string, required=True, help='密码格式不规范')
        parser.add_argument('code', type=identify_code_string, required=True, help='验证码格式不规范')
        args = parser.parse_args() # 获取参数

        check_code = self.validate_code(args.get('phone'), args.pop('code'))
        if check_code:
            raise VerificationCodeException()
        self.create_user(**args)
        return args


class LoginApi(Resource):
    """登录Api"""

    def post(self):
        pass

