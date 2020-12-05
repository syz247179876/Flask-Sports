# -*- coding: utf-8 -*-
# @Time  : 2020/12/2 下午11:41
# @Author : 司云中
# @File : auth-api.py
# @Software: Pycharm
from flask_restful import Resource, fields, reqparse
from pymongo.errors import DuplicateKeyError

from application.models.user_model import User

from application.utils.exception import VerificationCodeException
from application.utils.fields import IdentifyingCodeString, PasswordString, PhoneString, phone_string, password_string, \
    identify_code_string
from application.utils.redis import manager_redis, manager_redis_operation
from application.utils.success_code import response_code


class RegisterApi(Resource):
    """注册Api"""

    def create_user(self, **kwargs):
        """创建用户"""
        try:
            user = User(**kwargs)
            user.set_username(f"用户:{kwargs.get('phone')}")
            user.save()
            return user
        except DuplicateKeyError:
            return None


    def validate_code(self, phone, code):
        """验证校验码"""
        with manager_redis() as redis:
            redis_code = redis.get(phone)
            print(redis_code)
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
        if not check_code:
            # 验证码不正确
            raise VerificationCodeException()
        # 创建用户
        user = self.create_user(**args)
        return response_code.register_success if user else response_code.user_existed



class LoginApi(Resource):
    """登录Api"""

    def validate_code(self, phone, code):
        """验证验证码"""

        with manager_redis_operation() as manager:
            is_checked = manager.check_code(phone, code)

            if not is_checked:  # error
                return False, response_code.verification_code_error
            else:               # success
                return True, None


    def validate_password(self, phone, password):
        """验证密码"""

        # TODO: 查询mongodb,校验用户

        # if not is_correct:   # error
        #     return False, response_code.password_error
        # else:
        #     return True, None

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('phone', type=phone_string, required=True, help='手机号格式不正确')
        parser.add_argument('password', type=password_string, required=False, help='密码格式不规范')
        parser.add_argument('code', type=identify_code_string, required=False, help='验证码格式不正确')
        parser.add_argument('way', choices=('code', 'password'), required=True, help='必须选择登录方式')

        args = parser.parse_args()

        way = args.get('way')
        func_str = f"validate_{way}"
        func = getattr(self, func_str)
        is_validated, error = func(args.get('phone'),args.get(way))

        if is_validated: # 认证通过
            return response_code.login_success
        else:
            return error





