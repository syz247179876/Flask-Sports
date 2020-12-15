# -*- coding: utf-8 -*-
# @Time  : 2020/12/10 上午11:34
# @Author : 司云中
# @File : manager_api.py
# @Software: Pycharm
from flask import request
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

from application.models.integral_model import Commodity
from application.utils.exception import UploadFileOSSError
from application.utils.fields import commodity_string, integral_int, stock_int
from application.utils.success_code import response_code
from extensions.oss import oss


class IntegralManagerApi(Resource):
    """后台管理人员管理积分系统API"""

    def post(self):
        """添加商品"""

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=commodity_string, help="商品名格式不规范", required=True)
        parser.add_argument('integral', type=integral_int, help="积分值格式不规范", required=True)
        parser.add_argument('stock', type=stock_int, help="库存数据格式不规范", required=True)
        parser.add_argument('image', type=FileStorage, location='files', help="文件格式不规范",
                            required=True)  # 从请求体的files中拿数据
        args = parser.parse_args()
        outer_net = oss.upload_file(args.get('image'), 'IntegralCommdity')  # 上传文件到oss
        args.update({'image': outer_net})
        commodity = Commodity(**args)
        commodity.save()
        return response_code.add_commodity_success

    def delete(self):
        """删除商品"""

    def put(self):
        """更新商品信息"""
