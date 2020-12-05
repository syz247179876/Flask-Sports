# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 下午4:06
# @Author : 司云中
# @File : user_model.py
# @Software: Pycharm

from flask_mongoengine.wtf import model_form

from application.models.base import BaseModel
from mongoengine import *


class User(BaseModel):
    """用户模型"""

    # 用户名
    username = StringField(required=True, min_length=1, max_length=20, unique=True)
    # 手机号
    phone = StringField(required=True, regex=r'13[0-9]{9}|15[0-9]{9}', unique=True)
    # 密码
    password = StringField(required=True, max_length=20, min_length=8, regex=r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,20}$')
    # 积分值
    integral = IntField(default=0)
    # 头像
    head_image = URLField()

    def set_username(self, param):
        self.username = param


class Address(Document):
    """收货地址模型"""

    # 收货人
    consignee = StringField(max_length=15, required=True, min_length=1)

    # 手机号
    phone = StringField(max_length=11, min_length=11, required=True, regex=r'13[0-9]{9}|15[0-9]{9}')

    # 详细地址
    detail_address = StringField(max_length=128, required=True)

    # 是否是默认地址
    default = BooleanField(default=False)

    # 用户, 引用User文档
    user = ReferenceField(User)




