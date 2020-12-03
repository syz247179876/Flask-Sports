# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 下午2:23
# @Author : 司云中
# @File : sms_task.py
# @Software: Pycharm
import uuid
from application.utils.extensions import sms
from application.utils.extensions import celery_app as app
from wsgi import app

@app.task
def send_phone(phone_numbers, template_code, template_param):
    _business_id = uuid.uuid1()
    sms.send_sms(_business_id, phone_numbers=phone_numbers, sign_name=app.config.get('SIGN_NAME'), template_code=template_code,
             template_param=template_param)
