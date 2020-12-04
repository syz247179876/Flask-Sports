# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 下午4:06
# @Author : 司云中
# @File : user_model.py
# @Software: Pycharm

from flask_mongoengine.wtf import model_form


class User(db.Document):
    """用户模型"""

    username = db.StringField(required=True)
    phone = db.StringField(required=True)
    password = db.StringField(required=True)
    is_active