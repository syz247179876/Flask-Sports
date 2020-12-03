# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 上午10:22
# @Author : 司云中
# @File : extentions.py
# @Software: Pycharm

from application.utils.celery_app import PyCelery
from application.utils.redis import BaseRedis

celery_app = PyCelery()

redis_app = BaseRedis