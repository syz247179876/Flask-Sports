# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 下午3:09
# @Author : 司云中
# @File : send_code_api.py
# @Software: Pycharm
import random
import string

from flask_restful import Resource, reqparse

from application.utils.fields import phone_string
from application.utils.redis import manager_redis_operation
from application.signals.signal import send_code_signal
from application.utils.success_code import response_code
from configs.settings import TEMPLATES_CODE_REGISTER


def get_verification_code():
    """Custom verification code"""
    code = ''
    # 设置随机种子
    random.seed(random.randint(1, 100))
    for i in range(5):
        m = random.randrange(1, 9)
        if i == m:
            code += str(m)
        else:
            code += random.choice(string.ascii_uppercase)
    return code


class SendCodeApi(Resource):
    """发送验证码API"""

    def create_save_code(self, phone):
        """创建存储验证码"""

        code = get_verification_code()
        with manager_redis_operation() as manager:
            manager.save_code(phone, code, time=600)
        return code

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone', type=phone_string, required=True, help='手机号格式不正确')
        args = parser.parse_args()
        phone = args.get('phone')

        code = self.create_save_code(phone)

        send_code_signal.send(self, phone_numbers=phone, template_code=TEMPLATES_CODE_REGISTER,
                                  template_param={'code': code})
        return response_code.register_success
