# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 下午9:05
# @Author : 司云中
# @File : integral_model.py
# @Software: Pycharm
from mongoengine import *


class Commodity(Document):

    # 商品名
    name = StringField(required=True, max_length=50)

    # 兑换积分值
    integral = IntField(required=True, min_value=1)

    # 库存
    stock = IntField(required=True, min_value=1)

    # 图片
    head_image = URLField(required=True)
