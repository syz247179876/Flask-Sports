# -*- coding: utf-8 -*-
# @Time  : 2020/12/2 下午2:24
# @Author : 司云中
# @File : test_urls.py
# @Software: Pycharm
from flask import Blueprint
from flask_restful import Api

from application.auth.test_api import TestApi
from application.utils.json import output_json

test = Blueprint('tests', __name__, url_prefix='/test-api')
test_api = Api(test)

test_api.add_resource(TestApi, '/syzs', endpoint='testss')

# bp = Blueprint('auth', __name__, url_prefix='/auth')


# bp_api = Api(bp)
# bp_api.add_resource(TestApi, '/todo1', endpoint='todo666')  # 添加资源路由
# bp_api.representation(mediatype='application/json')(output_json)

test_api.representation(mediatype='application/json')(output_json)  # 自定义返回格式