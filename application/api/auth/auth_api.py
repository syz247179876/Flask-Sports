# -*- coding: utf-8 -*-
# @Time  : 2020/12/2 下午11:41
# @Author : 司云中
# @File : auth-api.py
# @Software: Pycharm


from flask import current_app
from flask_restful import Resource, reqparse
from mongoengine import NotUniqueError
from pymongo.errors import DuplicateKeyError

from application.signals.signal import generate_token_signal
from application.utils.exception import VerificationCodeException, CodeMissingError, \
    PasswordMissingError, ServerErrors, PasswordError, CodeError, UserExistedError
from application.utils.fields import phone_string, password_string, \
    identify_code_string
from extensions.hasher import make_password
from extensions.redis import manager_redis, manager_redis_operation
from application.utils.success_code import response_code


class RegisterApi(Resource):
    """注册Api"""

    CACHE_NAME = 'code'

    @staticmethod
    def create_user(**kwargs):
        """创建用户"""
        try:
            User = current_app.config.get('user')
            password = kwargs.pop('password')
            user = User(**kwargs)
            user.set_username(f"用户:{kwargs.get('phone')}")
            user.set_password(password)  # 加密
            user.save()
            return user
        except DuplicateKeyError:
            raise UserExistedError()
        except NotUniqueError:
            raise UserExistedError()

    def validate_code(self, phone, code):
        """验证校验码"""
        with manager_redis(self.CACHE_NAME) as redis:
            redis_code = redis.get(phone)
            if redis_code != code:
                return False
            return True

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)  # 定义请求解析器,捆绑所有错误统一返回给前端
        parser.add_argument('phone', type=phone_string, required=True, help='手机号格式不正确')
        parser.add_argument('password', type=password_string, required=True, help='密码格式不规范')
        parser.add_argument('code', type=identify_code_string, required=True, help='验证码格式不规范')
        args = parser.parse_args()  # 获取参数

        check_code = self.validate_code(args.get('phone'), args.pop('code'))
        if not check_code:
            # 验证码不正确
            raise VerificationCodeException()
        # 创建用户
        self.create_user(**args)
        return response_code.register_success


class LoginApi(Resource):
    """登录Api"""
    CACHE_NAME = 'code'

    def validate_code(self, phone, code):
        """验证验证码"""
        if not code:  # 丢失验证码
            raise CodeMissingError()

        with manager_redis_operation('code') as manager:
            is_checked = manager.check_code(phone, code)

            if not is_checked:  # code error
                raise CodeError()

            # 校验用户
            try:
                User = current_app.config.get('user')
                user = User.objects(phone=phone).first()  # json格式数据
                if user:
                    # 发送信号,获取token
                    token = generate_token_signal.send(self, id=user.id)[0][1]
                    return token  # 取结果
                else:
                    # 密码不正确
                    raise PasswordError()
            except Exception:
                # 服务器开小车去了
                raise ServerErrors()

    def validate_password(self, phone, raw_password):
        """验证密码"""
        if not raw_password:  # 丢失密码
            raise PasswordMissingError()
        password = make_password(raw_password)  # 加密
        try:
            User = current_app.config.get('user')
            user = User.objects(phone=phone, password=password).first()  # json格式数据
            if user:
                # 发送信号,获取token, 返回[(func, result)]
                token = generate_token_signal.send(self, id=user.id)[0][1]
                return token  # 取结果
            else:
                raise PasswordError()
        except Exception as e:
            # TODO: 日志记录
            print(e)
            raise ServerErrors()

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('phone', type=phone_string, required=True, help='手机号格式不正确')
        parser.add_argument('password', type=password_string, required=False, help='密码格式不规范')
        parser.add_argument('code', type=identify_code_string, required=False, help='验证码格式不正确')
        parser.add_argument('way', choices=('code', 'password'), required=True, help='必须选择正确的登录方式')
        args = parser.parse_args()

        way = args.get('way')
        func_str = f"validate_{way}"

        func = getattr(self, func_str)
        token = func(args.get('phone'), args.get(way))  # 获取token
        response_code.login_success.update({'token': token})  # 添加token
        return response_code.login_success
