# -*- coding: utf-8 -*-
# @Time  : 2020/12/6 下午2:22
# @Author : 司云中
# @File : sport_model.py
# @Software: Pycharm
import datetime

from application.models.user_model import User
from application.utils.extensions import db


class StepSport(db.Document):
    """运动步数模型"""
    meta = {
        'collection': 'step_sport'
    }

    user = db.ReferenceField(User)

    # 默认当天, 晚上11点定时任务
    date = db.DateField(default=datetime.datetime.utcnow().date())
    # 运动步数
    step = db.IntField(default=0)

    STATUS = (
        (1, 'Pretty Good'),
        (2, 'Preferably'),
        (3, 'Commonly'),
        (4, 'Just so so'),
        (5, 'To bad')
    )

    # 当日运动状态
    status = db.IntField(max_length=1, choices=STATUS, default=5)

    # 当日获得积分值
    integral = db.IntField(max_value=9999, default=0)

    # 当日运动目标
    GOAL = (
        (1, 3000),
        (2, 6000),
        (3, 10000),
        (4, 16000),
        (5, 21000),
        (6, 25000)
    )
    goal = db.IntField(choices=GOAL, default=1)
