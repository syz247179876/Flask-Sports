# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 上午2:20
# @Author : 司云中
# @File : handle_signal.py
# @Software: Pycharm


from application.signals.signal import send_code_signal
from application.tasks.user_task import send_phone

class CodeSignal(object):
    """处理发送验证码信号"""

    def register_task(self, celery):
        """注册任务"""
        tasks = {}
        tasks.update({send_phone.__name__: celery.task(send_phone)})  # 注册send_phone任务
        return tasks


    def init_app(self, app):
        send_code_signal.connect(send_phone)
        celery = app.config.get('CELERY_INSTANCE')  # 导入celery
        tasks = self.register_task(celery)
        setattr(app, 'tasks', tasks)









