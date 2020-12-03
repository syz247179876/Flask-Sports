# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 上午10:22
# @Author : 司云中
# @File : extensions.py
# @Software: Pycharm
from application.signals.handle_signal import CodeSignal
from application.utils.celery_app import PyCelery
from application.utils.redis import BaseRedis
from application.utils.sms import sms

code_signal = CodeSignal()   # signal

celery_app = PyCelery() # celery application

redis_app = BaseRedis   # redis application

sms = sms



