# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 下午4:14
# @Author : 司云中
# @File : base.py
# @Software: Pycharm


from flask_mongoengine.wtf import model_form

from mongoengine import *
from application.utils.hasher import make_password, check_password
import datetime

class BaseModel(Document):
    """基类模型"""

    meta = {'allow_inheritance': True}


    USERNAME_FIELD = 'username'

    is_active = BooleanField(default=True)

    is_admin = BooleanField(default=False)

    last_login = DateTimeField(required=True, default=datetime.datetime.now())

    register_time = DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.get_username()

    def get_username(self):
        """获取用户名"""
        return getattr(self, self.USERNAME_FIELD)

    @property
    def is_anonymous(self):
        """
        判断用户对象是否是匿名用户
        :return:
        """
        return False

    @property
    def is_authenticated(self):
        """判断用户是否认证通过"""
        return True

    def set_password(self, raw_password):
        """
        encrypt!
        :param raw_password:
        :return:
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password, update=True):
        """
        Firstly, checking password, if password doesn't correct, return False.
        Secondly, modifying password, if update attribute is set True
        :param raw_password:
        :return:
        """

        password = self.set_password(raw_password)  # 加密后密码
        checked = check_password(raw_password, password)
        if not checked:
            return False
        return True

    @classmethod
    def get_phone_field_name(cls):
        try:
            return cls.EMAIL_FIELD
        except AttributeError:
            return 'phone'
