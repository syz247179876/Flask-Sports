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

from application.api.Client.user import authenticate_jwt
from application.models.integral_model import Commodity
from application.utils.api_permission import api_permission_check
from application.utils.exception import IntegralInsufficientError, ServerError, DataUniversalException
from application.utils.fields import get_params_int
from application.utils.success_code import response_code


class IntegralEMallApi(Resource):
    """积分商城API"""


    commodity_fields = {
        'name': fields.String,
        'integral': fields.Integer,
        'stock': fields.Integer,
        'image': fields.String
    }

    resource_fields = {
        'commodity': fields.List(fields.Nested(commodity_fields))
    }

    def get_queryset(self, page, count):
        """获取所有商品"""
        commodity = Commodity.live_commodity()[(page-1)*count:page*count]  # 搜索所有数据
        return commodity

    @marshal_with(resource_fields)
    def get(self):
        """
        浏览商品,分页/流加载
        """
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=get_params_int, required=True, help='请求的参数不规范')
        parser.add_argument('count', type=get_params_int, required=False, help='请求的参数不规范')
        kwargs = parser.parse_args()
        if kwargs['count'] is None:
            kwargs.update({'count':10})  # 默认每次显示10个商品,如果未提供的话

        commodity = self.get_queryset(**kwargs)
        data = [i for i in commodity]
        return {'commodity': data}

    @authenticate_jwt
    @api_permission_check
    def post(self):
        """兑换商品"""
        parser = reqparse.RequestParser()
        parser.add_argument('commodity', type=str, required=True, help='商品数据格式不正确')
        kwargs = parser.parse_args()
        try:
            commodity = Commodity.objects(id=ObjectId(kwargs.get('commodity'))).first()
            if commodity:
                commodity_integral = commodity.get_integral()  # 获取目标商品积分值
                user = getattr(g, 'user')
                if user.integral > commodity_integral:  # 用户的积分值大于该商品
                    # 更新用户积分值
                    user.update({'integral': user.integral - commodity_integral})
                    user.save()
                else:
                    raise IntegralInsufficientError()
        except InvalidId:
            # ObjectId转化异常
            raise DataUniversalException()
        else:
            return response_code.exchange_success
