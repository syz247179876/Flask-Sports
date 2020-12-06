# -*- coding: utf-8 -*-
# @Time  : 2020/12/6 上午8:50
# @Author : 司云中
# @File : sport_api.py
# @Software: Pycharm

from flask_restful import Resource
from flask import g

from application.api.auth import authenticate_jwt


class TimerSportApi(Resource):
    """设定运动定时任务API"""
    pass

class RankApi(Resource):
    """当天运动排名API"""
    pass

class CounterApi(Resource):
    """当天实时获取当前用户的计数器步数"""
    method_decorators = [authenticate_jwt]

    def get(self):
        user = getattr(g, 'user')  # 获取用户对象
        return user


