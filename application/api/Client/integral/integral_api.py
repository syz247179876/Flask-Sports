# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 下午9:04
# @Author : 司云中
# @File : exchange_api.py
# @Software: Pycharm

"""兑换商品API"""
from bson import ObjectId
from bson.errors import InvalidId
from flask import g
from flask_restful import Resource, fields, marshal_with, reqparse
from application.models.integral_model import Commodity
from application.utils.exception import IntegralInsufficientError, ServerError, DataUniversalException
from application.utils.success_code import response_code


class IntegralEMallApi(Resource):
    """积分商城API"""

    commodity_fields = {
        'name': fields.String,
        'integral': fields.Integer,
        'stock':fields.Integer,
        'image':fields.String
    }

    resource_fields = {
        'commodity':fields.List(fields.Nested(commodity_fields))
    }

    def get_queryset(self):
        """获取所有商品"""
        commodity = Commodity.live_commodity()  # 搜索所有数据
        return commodity

    @marshal_with(resource_fields)
    def get(self):
        """浏览商品"""
        commodity = self.get_queryset()
        data = [i for i in commodity]

        return {'commodity':data}


    def post(self):
        """兑换商品"""
        parser = reqparse.RequestParser()
        parser.add_argument('commodity', type=str, required=True, help='商品数据格式不正确')
        args = parser.parse_args()
        try:
            commodity = Commodity.objects(id=ObjectId(args.get('commodity'))).first()
            print(commodity)
            if commodity:
                commodity_integral = commodity.get_integral() # 获取目标商品积分值
                user = getattr(g, 'user')
                if user.integral > commodity_integral: # 用户的积分值大于该商品
                    # 更新用户积分值
                    user.update({'integral':user.integral-commodity_integral})
                    user.save()
                else:
                    raise IntegralInsufficientError()
        except InvalidId:
            # ObjectId转化异常
            raise DataUniversalException()
        # except Exception:
        #     raise ServerError()
        else:
            return response_code.exchange_success
