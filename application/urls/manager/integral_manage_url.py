# -*- coding: utf-8 -*-
# @Time  : 2020/12/13 下午5:54
# @Author : 司云中
# @File : integral_manage_url.py
# @Software: Pycharm

from flask_restful import Api
from flask import Blueprint

from application.api.manager.integral_manager.integral_manager_api import IntegralManagerApi
from application.utils.json import output_json


integral_manager = Blueprint('integral_manager_emall', __name__, url_prefix='/emall-manager-api')

integral_manager_api = Api(integral_manager)

integral_manager_api.add_resource(IntegralManagerApi, '/integral-api', endpoint='integral')

integral_manager_api.representation('application/json')(output_json)