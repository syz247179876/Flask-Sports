# -*- coding: utf-8 -*-
# @Time  : 2020/12/6 上午8:50
# @Author : 司云中
# @File : sport_api.py
# @Software: Pycharm
import datetime
import json

from bson import ObjectId
from flask import g, current_app
from flask_restful import Resource, fields, marshal_with, reqparse

from application.api.Client.user import authenticate_jwt
from application.models.sport_model import StepSport
from application.utils.api_permission import api_permission_check
from extensions.redis import manager_redis_operation


class RankApi(Resource):
    """当天运动排名API"""

    CACHE_NAME = 'whole'

    method_decorators = [authenticate_jwt, api_permission_check]

    others_fields = {
        'username': fields.String,
        'step': fields.Integer,
        'head_image': fields.String,
        'rank': fields.Integer
    }

    resource_fields = {
        'username': fields.String,
        'step': fields.Integer,
        'head_image': fields.String,
        'rank': fields.Integer,
        'others': fields.List(fields.Nested(others_fields))
    }

    @marshal_with(resource_fields)
    def get(self):
        """获取当天运动排名API"""
        user = getattr(g, 'user')

        with manager_redis_operation() as manager:
            individual_rank = manager.retrieve_cur_rank_user(user.id, mold='step', redis_name=self.CACHE_NAME)
            whole_rank = manager.retrieve_cur_rank('step',redis_name=self.CACHE_NAME)

        whole_list = []
        # 解析sorted set,生成user数据,序列化对象
        level = 1
        for single in whole_rank:
            dicts = {}
            user_id = single[0].decode()
            user = current_app.config.get('user').objects(id=ObjectId(user_id)).first()
            dicts.update({
                'username': user.get_username(),
                'head_image': user.head_image,
                'step':single[1],
                'rank':level  # 排名
            })
            level += 1
            whole_list.append(dicts)

        data = json.loads(user.to_json())
        # 生成最终数据
        data.update({
            'rank': individual_rank[0] + 1,  # redis取 排名第一为0
            'step': individual_rank[1],
            'others': whole_list
        })
        return data


class CounterApi(Resource):
    """
    当天实时获取当前用户的计数器步数
    """
    CACHE_NAME = 'user'
    CACHE_NAME_ANOTHER = 'whole'

    method_decorators = [authenticate_jwt, api_permission_check]

    resource_fields = {
        'username': fields.String,
        'integral': fields.Integer,
        'is_active': fields.Boolean(attribute='is_active'),  # 指向数据对象中真正的值,换名
        'phone': fields.String,
        'head_image': fields.String(default='https://flask-sports.oss-cn-beijing.aliyuncs.com/1579793244834816.jpg'),
        'step': fields.Integer
    }

    @marshal_with(resource_fields)
    def get(self):
        """显示用户步数"""
        user = getattr(g, 'user')  # 获取用户对象
        with manager_redis_operation() as manager:
            step = manager.get_sport_value(str(user.id), datetime.datetime.now().strftime('%Y-%m-%d'), mold='step',
                                           redis_name=self.CACHE_NAME)
            step = step if step else 0
            user_dict = json.loads(user.to_json())
            user_dict.update({'step': step})
            return user_dict

    def post(self):
        """保存用户步数"""
        parser = reqparse.RequestParser()
        parser.add_argument('step', type=int, required=True, help='步数格式不正确')
        args = parser.parse_args()
        user = getattr(g, 'user')
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        with manager_redis_operation() as manager:
            # 设置用户步数,并更新全服运动值榜
            manager.set_sport_value(user.id, today, args.get('step'), 'step', self.CACHE_NAME)
            manager.update_whole_rank(user.id, today, args.get('step'), 'step', self.CACHE_NAME_ANOTHER)
            return {'step_status': True}, 204


class ListCounterApi(Resource):
    """获取用户前7天的运动步数数据"""
    method_decorators = [authenticate_jwt, api_permission_check]

    sports_fields = {
        'step': fields.Integer,
        'date': fields.String,
        'status': fields.String,
        'goal': fields.String,
        'member_rank': fields.String,
        'is_member': fields.Boolean
    }

    resource_fields = {
        'username': fields.String,
        'head_image': fields.String(default='https://flask-sports.oss-cn-beijing.aliyuncs.com/1579793244834816.jpg'),
        'sport_data': fields.List(fields.Nested(sports_fields))  # 整体块嵌套
    }

    @staticmethod
    def generate_data(sport_instances):
        """
        生成适合的数据
        返回list数据

        example:
        data_list:[{'date': datetime.date(2020, 12, 6), 'stop': 232, 'status': 4, 'goal': 1}]
        date_list:[datetime.date(2020, 12, 6)]
        total_dict:
         "sport_data": {
                "2020-12-06": {
                    "date": "2020-12-06",
                    "stop": 232,
                    "status": 4,
                    "goal": 1
                }
            },
        total_list:
         "sport_data": [
            {
                "2020-12-06": {
                    "date": "2020-12-06",
                    "stop": 232,
                    "status": 4,
                    "goal": 1
                }
            }
        ],

        """
        data_list = []  # 数据表 ,用value
        date_list = []  # 日期表 ,用于key
        total_dict = {}  # 总数据字典, 由前两个生成
        total_list = []
        for instance in sport_instances:
            data_dict = {
                'date': instance.date.strftime('%Y-%m-%d'),  # 日期
                'step': instance.step,  # 运动步数
                'status': instance.status_display,  # 运动状态
                'goal': instance.goal_display,  # 运动目标
                'member_rank': instance.member_display,  # 获取会员等级
                'is_member': instance.is_member,  # 是否是会员
            }
            data_list.append(data_dict)
            date_list.append(instance.date.strftime('%Y-%m-%d'))
        for date, data in zip(date_list, data_list):
            total_dict.setdefault(date, data)
            total_list.append(total_dict)
        return total_list

    # @marshal_with(resource_fields)
    def get(self):
        """获取用户前7天的运动步数数据"""
        user = getattr(g, 'user')
        last_week = datetime.datetime.utcnow().date() - datetime.timedelta(days=6)
        sport_instances = StepSport.objects(user=user.id, date__gte=last_week).limit(7)
        sport_data = self.generate_data(sport_instances)
        data = {'sport_data': sport_data, 'username': user.username, 'head_image': user.head_image}
        return data
