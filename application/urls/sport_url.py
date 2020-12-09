# -*- coding: utf-8 -*-
# @Time  : 2020/12/6 上午8:34
# @Author : 司云中
# @File : sports_url.py
# @Software: Pycharm

from flask_restful import Api
from flask import Blueprint
from application.utils.json import output_json
from application.api.sport.sport_api import RankApi, CounterApi, ListCounterApi

sport = Blueprint('sport', __name__, url_prefix='/sport-api')

sport_api = Api(sport)

sport_api.add_resource(RankApi, '/rank-api', endpoint='rank')  # 排名API
sport_api.add_resource(CounterApi, '/counter-api', endpoint='counter')  # 步数计数器API
sport_api.add_resource(ListCounterApi, '/counter-list-api', endpoint='list-counter') # 一段时间的运动情况


sport_api.representation('application/json')(output_json)
