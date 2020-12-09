# -*- coding: utf-8 -*-
# @Time  : 2020/12/6 下午2:22
# @Author : 司云中
# @File : sport_model.py
# @Software: Pycharm
import datetime
from application.models.user_model import User
from extensions.database import db


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

    MEMBER = (
        (3,'铂金会员'),
        (2,'高级会员'),
        (1,'普通用户')
    )

    # 是否是会员
    is_member = db.BooleanField(default=False)

    # 会员等级
    member_rank = db.IntField(default=1, choices=MEMBER)

    @property
    def member_display(self):
        """获取会员等级可读数据"""
        dicts = {i[0]: i[1] for i in self.MEMBER}
        return dicts.get(self.member_rank)

    @property
    def goal_display(self):
        """获取目标可读数据"""
        dicts = {i[0]: i[1] for i in self.GOAL}
        return dicts.get(self.goal)

    @property
    def status_display(self):
        dicts = {i[0]: i[1] for i in self.STATUS}
        return dicts.get(self.status)
