# -*- coding: utf-8 -*-
# @Time  : 2020/12/9 下午10:17
# @Author : 司云中
# @File : emall_url.py
# @Software: Pycharm

from flask_restful import Api
from flask import Blueprint

from application.api.integral.integral_api import IntegralEMallApi
from application.utils.json import output_json


integral = Blueprint('integral_emall', __name__, url_prefix='/integral-api')

integral_api = Api(integral)
integral_api.add_resource(IntegralEMallApi, '/integral-api', endpoint='integral')

integral_api.representation('application/json')(output_json)