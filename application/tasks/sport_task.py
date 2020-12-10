# -*- coding: utf-8 -*-
# @Time  : 2020/12/5 下午3:37
# @Author : 司云中
# @File : sport_task.py
# @Software: Pycharm


"""运动任务"""
from bson import ObjectId

from application.models.user_model import User
from extensions.redis import manager_redis_operation
from application.models.sport_model import StepSport

CACHE_NAME = 'user'

def compute_integral(step):
    """
    计算积分值
    integral = step / 100
    """
    return step // 100

def calculation_status(step):
    """
    推算出当日运动状态
    :param step:
    :return:
    """

    # status = ['Pretty Good', 'Preferably', 'Commonly', 'Just so so', 'To bad']
    point = [25000, 16000, 9000, 3000, step]
    point.sort(reverse=True)
    return point.index(step) + 1

def timer_rewrite_step_number(mold):
    """
    定时从redis写回mongodb
    """

    with manager_redis_operation() as manager:
        result_dict = manager.rewrite_data_to_mongo(mold=mold, redis_name=CACHE_NAME)
        for member, value in result_dict.items():
            if not isinstance(member, str) or not isinstance(value, int):
                member = str(member.decode())  # 解码--->str--->_id
                value = int(value)
            try:
                user = User.objects(id=ObjectId(member)).first() # 获取user对象
                step = {
                        'integral': compute_integral(value),
                        'step': value,
                        'status': calculation_status(value),
                        'user': user
                    }
                StepSport(**step).save()           # 创建目标用户当天的运动记录
            except Exception as e:
                # TODO:日志记录/邮件通知
                print(e)
        print('同步成功')









