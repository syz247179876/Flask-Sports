# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 上午10:22
# @Author : 司云中
# @File : extensions.py
# @Software: Pycharm
from extensions.celery_app import PyCelery
from extensions.crypto import PBKDF2PasswordHasher
from extensions.redis import BaseRedis, RateRedis
from extensions.sms import sms


redis_app = BaseRedis   # redis application
rate_redis = RateRedis

sms = sms               # sms service

encryption =  PBKDF2PasswordHasher()  # PBKDF2 encryption



