# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 下午9:05
# @Author : 司云中
# @File : integral_model.py
# @Software: Pycharm
from mongoengine import *


class Commodity(Document):

    meta = {
        'collection': 'commodity'
    }

    # 商品名
    name = StringField(required=True, max_length=50)

    # 兑换积分值
    integral = IntField(required=True, min_value=1)

    # 库存
    stock = IntField(required=True, min_value=1)

    # 图片
    image = URLField(required=True)

    # 商品状态,上架/下架
    status = BooleanField(required=True)

    @queryset_manager    # 返回QuerySetManager对象
    def live_commodity(doc_cls, queryset):
        return queryset.filter(status=True)


    def get_name(self):
        """获取积分商品"""
        return self.name

    def get_integral(self):
        """获取商品所需积分值"""
        return self.integral

    def get_stock(self):
        """获取商品库存"""
        return self.stock

    def get_image(self):
        """获取商品大图片"""
        return self.image
