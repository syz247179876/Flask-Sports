# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 上午2:20
# @Author : 司云中
# @File : handle_signal.py
# @Software: Pycharm


from application.signals.signal import send_code_signal
from application.tasks.user_task import send_phone
from flask import session, current_app
from application.utils.exception import SessionUserInformationException
from application.signals.signal import update_session_user_signal, generate_token_signal
import jwt
import datetime

def update_session_user(sender, **kwargs):
    """
    update information of user in session
    any information need to update should be embedded in kwargs
    """
    user = session.get('user', None)
    if not user:
        raise SessionUserInformationException()
    user.update(kwargs)
    session['user'] = user

def generate_token(sender, **kwargs):
    """
    Generate token for user with payload which includes id and phone of current user
    """
    from bson import ObjectId
    # 设置token颁发后7天过期

    secret = current_app.config.get('SECRET')
    issuer = current_app.config.get('ISSUER')


    # 12-byte binary representation of instance of ObjectId
    kwargs.update({'id':str(kwargs.get('id'))})
    kwargs.update({
        'exp':datetime.datetime.utcnow() + datetime.timedelta(7),
        'iss':issuer  # 发行人
    })

    token = jwt.encode(kwargs, secret, algorithm='HS256')
    return token.decode()


class Signal(object):
    """处理发送验证码信号"""

    def register_task(self, celery):
        """注册任务"""
        tasks = {}
        tasks.update({send_phone.__name__: celery.task(send_phone)})  # 注册send_phone任务
        return tasks

    def configure_celery(self, app):
        """配置celery"""
        celery = app.config.get('CELERY_INSTANCE')  # 导入celery
        tasks = self.register_task(celery)
        setattr(app, 'tasks', tasks)

    def register_signal(self, signal, callback):
        """注册信号"""
        signal.connect(callback)

    def init_app(self, app):
        self.register_signal(send_code_signal, send_phone)  # 注册发送验证码信号
        self.register_signal(update_session_user_signal, update_session_user)  # 注册更新session用户信息信号
        self.register_signal(generate_token_signal, generate_token)      # 生成token
        self.configure_celery(app)
