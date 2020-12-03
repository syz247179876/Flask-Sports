# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 上午4:06
# @Author : 司云中
# @File : task.py
# @Software: Pycharm
import uuid

from application.utils.sms import sms


def send_phone(phone_numbers, template_code, template_param):
    """发送手机验证码"""
    _business_id = uuid.uuid1()
    sms.send_sms(_business_id, phone_numbers=phone_numbers, sign_name='SIGN_NAME', template_code=template_code,
             template_param=template_param)