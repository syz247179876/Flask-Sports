# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:26
# @Author : 司云中
# @File : __init__.py.py
# @Software: Pycharm


import functools

from flask import session, g
from application.utils.exception import AuthenticationError


def authenticate_session(func):
    """session认证用户是否登录"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user', None):
            return func(*args, **kwargs)
        raise AuthenticationError()
    return wrapper

def authenticate_jwt(func):
    """jwt认证用户是否登录"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 用户既存在,且is_authenticated为True
        if getattr(g, 'user', None) and getattr(g, 'user').is_authenticated:
            return func(*args, **kwargs)
        raise AuthenticationError()
    return wrapper
