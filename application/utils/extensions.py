# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 上午10:22
# @Author : 司云中
# @File : extensions.py
# @Software: Pycharm
from flask_mongoengine import MongoEngine

from application.signals.handle_signal import Signal
from application.utils.celery_app import PyCelery
from application.utils.crypto import PBKDF2PasswordHasher
from application.utils.redis import BaseRedis
from application.utils.sms import sms



celery_app = PyCelery() # celery application

redis_app = BaseRedis   # redis application

signal = Signal()   # signal

sms = sms               # sms service

db = MongoEngine()      # mongodb database


encryption =  PBKDF2PasswordHasher()  # PBKDF2 encryption



