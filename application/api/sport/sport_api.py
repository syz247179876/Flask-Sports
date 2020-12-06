# -*- coding: utf-8 -*-
# @Time  : 2020/12/6 上午8:50
# @Author : 司云中
# @File : sport_api.py
# @Software: Pycharm
import datetime
import json

from flask_restful import Resource, fields, marshal_with
from flask import g

from application.api.auth import authenticate_jwt
from application.utils.redis import manager_redis, manager_redis_operation


class TimerSportApi(Resource):
    """设定运动定时任务API"""
    pass

class RankApi(Resource):
    """当天运动排名API"""
    pass

class CounterApi(Resource):
    """当天实时获取当前用户的计数器步数"""
    method_decorators = [authenticate_jwt]

    resource_fields = {
        'username': fields.String,
        'integral': fields.Integer,
        'is_active': fields.Boolean(attribute='is_active'),  # 指向数据对象中真正的值,换名
        'phone': fields.String,
        'head_image': fields.String(default='https://flask-sports.oss-cn-beijing.aliyuncs.com/1579793244834816.jpg'),
        'step':fields.Integer
    }

    @marshal_with(resource_fields)
    def get(self):
        user = getattr(g, 'user')  # 获取用户对象
        with manager_redis_operation() as manager:
            step = manager.get_step(user.id, datetime.datetime.now().strftime('%Y-%m-%d'))
        user_dict = json.loads(user.to_json())
        user_dict.update({'step':step})
        return user_dict
