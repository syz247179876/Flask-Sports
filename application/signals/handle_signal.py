# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 上午2:20
# @Author : 司云中
# @File : handle_signal.py
# @Software: Pycharm


import datetime
import json
import time

import jwt
from bson import ObjectId
from flask import session, current_app, request_started, request_finished, g
from flask.globals import request
from jwt.exceptions import ExpiredSignatureError, DecodeError

from application.signals.signal import send_code_signal
from application.signals.signal import update_session_user_signal, generate_token_signal
from application.tasks.user_task import send_phone
from application.utils.exception import SessionUserInformationException, ServerTokenExpire, TokenDecodeError
from application.utils.redis import manager_redis_operation


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
    # 设置token短期存活1天
    expire_day = current_app.config.get('JWT_EXPIRE_DAY', 1)
    # 刷新时间
    refresh_day = current_app.config.get('JWT_REFRESH_DAY', 7)

    secret = current_app.config.get('SECRET')
    issuer = current_app.config.get('ISSUER')
    # 颁发时间
    start_time = datetime.datetime.utcnow()
    # 过期时间
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(days=expire_day)
    # 刷新有效期
    refresh_time = datetime.datetime.utcnow() + datetime.timedelta(days=refresh_day)

    # 12-byte binary representation of instance of ObjectId
    kwargs.update({'id': str(kwargs.get('id'))})
    kwargs.update({
        'exp': expire_time,
        'iss': issuer  # 发行人
    })

    # 生成token
    token = jwt.encode(kwargs, secret, algorithm='HS256')

    # 存入redis,便于根据最终过期刷新token
    with manager_redis_operation() as manager:
        manager.save_token_kwargs(id=kwargs.get('id'), token=token, start_time=time.mktime(start_time.timetuple()),
                                  refresh_time=time.mktime(refresh_time.timetuple()))
    return token.decode()


def record_ip(host):
    """记录目标用户ip"""

    with manager_redis_operation() as manager:
        ip, port = host.split(':')
        manager.record_ip(ip)


def again_token(payload=None, id=None):
    """再次生成token"""
    with manager_redis_operation() as manager:
        refresh_time = manager.get_token_exp(id)  # 获取token最终失效期
    now = time.mktime(datetime.datetime.now().timetuple())
    if refresh_time > now:
        # 表明此时应刷新生成新的token
        secret = current_app.config.get('SECRET')
        token = jwt.encode(payload, secret, algorithm='HS256')
        return token
    else:
        raise ServerTokenExpire()


def parse_jwt(sender, **kwargs):
    """
    Parse token from client
    then, generate new user instance, which would be assigned to flask.g
    """
    User = current_app.config.get('user')
    global id, payload
    expire_day = current_app.config.get('JWT_EXPIRE_DAY', 1)

    # 获取当前代理request
    req = request
    # req = _request_ctx_stack.top.request
    record_ip(req.headers.get('host'))  # 记录用户IP
    token = req.headers.get('Bearer-Token', None)  # 获取token
    if token:
        try:
            payload = jwt.decode(token, key=current_app.config.get('SECRET'), issuer=current_app.config.get('ISSUER'),
                                 leetway=datetime.timedelta(days=expire_day),
                                 algorithms='HS256')
            id = payload.get('id')  # 拿到用户id
            g.user = User.objects(id=ObjectId(id)).first()  # 创建用户对象赋值给全局代理对象g.user,以后通过g.user判断当前用户是否认证!
        except ExpiredSignatureError:
            # 在解析payload过程中突然过期,重新生成
            # token到期异常,判断refresh_jwt是否还在有效期
            token = again_token(payload, id)
            # 添加到headers
            req.headers['Bearer-Token'] = token
            req['token'] = token  # 暂时存放,等执行完视图函数,添加到Response中
        except DecodeError:
            # token错误
            raise TokenDecodeError()


def append_jwt(sender, response):
    """
    如果request中存在token的话,则将token添加到response
    1.解码,获取str类型的Response数据
    2.更新token到Response数据
    3.编码,写回response.__dict__
    """
    req = request
    try:
        # 刷新重新写回token到Response的情况
        if getattr(req, 'token', None):
            print(response.__dict__)
            response_str = response.__dict__.get('response')[0].decode()
            response_dict = json.loads(response_str)
            response_dict.update({'token': getattr(req, 'token')})
            response_str = json.dumps(response_dict)
            response.__dict__.get('response')[0] = response_str.encode()
    except TypeError:
        # 处理特殊Response对象属性的情况
        pass
    except AttributeError:
        # 处理没有token字段的情况
        pass


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
        self.register_signal(generate_token_signal, generate_token)  # 生成token
        self.register_signal(request_started, parse_jwt)  # 解析jwt,获取用户对象,立即登入
        self.register_signal(request_finished, append_jwt)  # 追加jwt
        self.configure_celery(app)
