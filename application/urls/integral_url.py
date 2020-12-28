# -*- coding: utf-8 -*-
# @Time  : 2020/12/9 下午10:17
# @Author : 司云中
# @File : emall_url.py
# @Software: Pycharm

from flask_restful import Api
from flask import Blueprint
from flask_restful_swagger import swagger
from application.api.Client.integral.integral_api import IntegralEMallApi

from application.utils.json import output_json

integral = Blueprint('integral_emall', __name__, url_prefix='/emall-api', )

# integral_api = swagger.docs(
#     Api(integral),
#     apiVersion='0.1',
#     basePath='http://127.0.0.1:5001/',
#     produces=["application/json", "text/html"]
# )

integral_api = Api(integral)
integral_api.add_resource(IntegralEMallApi, '/integral-api', endpoint='integral')

integral_api.representation('application/json')(output_json)
