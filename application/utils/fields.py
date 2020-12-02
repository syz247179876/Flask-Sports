# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 上午12:22
# @Author : 司云中
# @File : fields.py
# @Software: Pycharm

from flask_restful import fields
import re

class PhoneString(fields.Raw):
    # 构建手机号字段
    def format(self, value):
        if len(value) != 11 or re.match(r'13[0-9]{9}|15[0-9]{9}', value) is None:
            raise ValueError('手机号格式不合法')
        return value

class PasswordString(fields.Raw):
    """构建密码字段"""
    def format(self, value):
        if len(value) < 8 or len(value) > 20 or re.match(r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,20}$', value) is None:
            raise ValueError('密码至少包含 数字和英文，长度6-20,不能出现非法字符')
        return value

class IdentifyingCodeString(fields.Raw):
    """构建验证码字段"""
    def format(self, value):
        if re.match(r'^[0-9A-Za-z]{6}', value) is None:
            raise ValueError('验证码格式不正确')
        return value