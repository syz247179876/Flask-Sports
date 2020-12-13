# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 下午4:06
# @Author : 司云中
# @File : user_model.py
# @Software: Pycharm
import datetime

from extensions.database import db
from extensions.hasher import make_password, check_password

from mongoengine import *


# 使用flask_mongoengine, 扩充mongoengine,提供与flask的结合管理
class User(db.Document):
    """用户模型"""

    # 元属性,创建类之间修改类,增添索引
    meta = {
        'collection': 'user',
        'indexes': [
            'phone',
        ],
        'ordering': ['-register_time']  # 按顺序显示

    }

    # 用户名
    username = db.StringField(required=True, min_length=1, max_length=20, unique=True)
    # 手机号
    phone = db.StringField(required=True, regex=r'13[0-9]{9}|15[0-9]{9}', unique=True)
    # 密码
    password = db.StringField(required=True, max_length=128)
    # 积分值
    integral = db.IntField(default=0)
    # 头像
    head_image = db.URLField(required=False,
                             default='https://flask-sports.oss-cn-beijing.aliyuncs.com/1579793244834816.jpg')
    # 账户是否可用
    is_active = db.BooleanField(default=True)
    # 是否具备管理员权限
    is_admin = db.BooleanField(default=False)
    # 上次登录时间
    last_login = db.DateTimeField(required=True, default=datetime.datetime.now())
    # 注册时间
    register_time = db.DateTimeField(default=datetime.datetime.now())
    # 兴趣关键词组
    appetition = db.ListField(StringField(max_length=5, required=False))

    USERNAME_FIELD = 'username'

    PHONE_FILED = 'phone'

    def __str__(self):
        return self.get_username()

    def __repr__(self):
        return f'用户:<{self.get_username()}>'

    def set_username(self, param):
        self.username = param

    def get_appetition(self):
        """获取用户兴趣"""
        return self.appetition

    def get_identity(self):
        """用户唯一标识"""
        return self.id

    def get_phone(self):
        return getattr(self, self.PHONE_FILED)

    def get_username(self):
        """获取用户名"""
        return getattr(self, self.USERNAME_FIELD)

    def get_head_image(self):
        """获取头像"""
        return self.head_image

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
        return self.password

    def check_password(self, raw_password):
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

    def check_permission(self):
        """检查基本权限"""
        return self.is_active

    def check_superuser_permission(self):
        """检查是否具备管理员的权限"""
        return self.is_active and self.is_admin

    def save_head_image_url(self, file_url):
        """
        保存文件URL
        :param file_url: 远程文件地址
        """
        self.head_image = file_url
        self.save()

    def save_head_image(self, filename):
        """
        保存文件名
        :param filename: 文件名
        """
        self.head_image = filename
        self.save()


class Address(db.Document):
    """收货地址模型"""

    meta = {
        'collection': 'address'
    }
    # 收货人
    consignee = db.StringField(max_length=15, required=True, min_length=1)

    # 手机号
    phone = db.StringField(max_length=11, min_length=11, required=True, regex=r'13[0-9]{9}|15[0-9]{9}')

    # 详细地址
    detail_address = db.StringField(max_length=128, required=True)

    # 是否是默认地址
    default = db.BooleanField(default=False)

    # 用户, 引用User文档, 一对多,一个用户多个地址
    user = db.ListField(db.ReferenceField(User, reverse_delete_rule=db.CASCADE))
