# -*- coding: utf-8 -*-
# @Time  : 2020/12/6 上午8:50
# @Author : 司云中
# @File : sport_api.py
# @Software: Pycharm
import datetime
import json

from flask import g
from flask_restful import Resource, fields, marshal_with, reqparse
from mongoengine import NotUniqueError, ValidationError
from pymongo.errors import DuplicateKeyError

from application.api.auth import authenticate_jwt
from application.models.sport_model import StepSport
from application.utils.exception import MongodbValidationError
from application.utils.redis import manager_redis_operation


class TimerSportApi(Resource):
    """设定运动定时任务API"""
    pass


class RankApi(Resource):
    """当天运动排名API"""
    method_decorators = [authenticate_jwt]

    user_fields = {
        'username': fields.String,
        'step': fields.String,
        'head_image': fields.String
    }

    resource_fields = {
        'rank_situation': fields.List(fields.Nested(user_fields))
    }

    def get(self):
        """获取当天运动排名API"""
        user = getattr(g, 'user')

        with manager_redis_operation() as manager:
            user_rank = manager.retrieve_cur_rank_user(user.id)
            # manager.retrieve_rank_list(user.id)
        print()


class CounterApi(Resource):
    """
    当天实时获取当前用户的计数器步数
    """
    method_decorators = [authenticate_jwt]

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
            step = manager.get_step(user.id, datetime.datetime.now().strftime('%Y-%m-%d'))
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
            status = manager.set_sport_value(user.id, today, args.get('step'), 'step')
        return {'step_status': status}, 204


class ListCounterApi(Resource):
    """获取用户前7天的运动步数数据"""
    method_decorators = [authenticate_jwt]


    sports_fields = {
        'step': fields.Integer(),
        'date': fields.String(),
        'status': fields.Integer(),
        'goal': fields.Integer()
    }

    resource_fields = {
        'username': fields.String(),
        'head_image': fields.String(default='https://flask-sports.oss-cn-beijing.aliyuncs.com/1579793244834816.jpg'),
        'sport_data': fields.List(fields.Nested(sports_fields))  # 整体块嵌套
    }

    def generate_data(self, sport_instances):
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
                'stop': instance.step,  # 运动状态
                'status': instance.status,  # 运动状态
                'goal': instance.goal  # 运动目标
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
        data = {'sport_data':sport_data, 'username':user.username, 'head_image':user.head_image}
        return data


class RecordTodayStepSport(Resource):
    """
    定时任务,记录用户当天的运动情况
    将redis中的步数取出,构建StepSport对象,写回mongodb
    每晚11点触发
    """

    method_decorators = [authenticate_jwt]

    def compute_integral(self, step):
        """
        计算积分值
        integral = step / 100
        """
        return step // 100

    def calculation_status(self, step):
        """
        推算出当日运动状态
        :param step:
        :return:
        """

        # status = ['Pretty Good', 'Preferably', 'Commonly', 'Just so so', 'To bad']
        point = [25000, 16000, 9000, 3000, step]
        point.sort(reverse=True)
        return point.index(step) + 1

    def get(self):
        """异步任务,请求模拟异步任务写回"""
        data_dict = {}
        user = getattr(g, 'user')
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        with manager_redis_operation() as manager:
            step = manager.get_sport_value(user.id, today, 'step')
            print(step)

        data_dict.update(
            {
                'integral': self.compute_integral(step),
                'step': step,
                'status': self.calculation_status(step),
                'user': user
            },
        )
        try:
            step_sport = StepSport(**data_dict).save()
            return step_sport
        except DuplicateKeyError:
            return MongodbValidationError()
        except NotUniqueError:
            raise MongodbValidationError()
        except ValidationError:
            raise MongodbValidationError()
