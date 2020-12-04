# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 上午10:22
# @Author : 司云中
# @File : extensions.py
# @Software: Pycharm
from application.signals.handle_signal import CodeSignal
from application.utils.celery_app import PyCelery
from application.utils.crypto import PBKDF2PasswordHasher
from application.utils.redis import BaseRedis
from application.utils.sms import sms
from flask_mongoengine import MongoEngine

celery_app = PyCelery() # celery application

redis_app = BaseRedis   # redis application

code_signal = CodeSignal()   # signal

sms = sms               # sms service

db = MongoEngine()      # mongodb database

encryption =  PBKDF2PasswordHasher()  # PBKDF2 encryption



