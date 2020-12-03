# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 上午9:50
# @Author : 司云中
# @File : celery_app.py
# @Software: Pycharm

from __future__ import absolute_import, unicode_literals
from celery import Celery

class PyCelery(object):
    """Manages the creation of celery for your Flask app"""


    def __init__(self, app=None, name=None, config=None, *args, **kwargs):
        if app is not None:
            self.init_app(app, name, config, *args, **kwargs)

    def init_app(self, app, name=None, config=None, *args, **kwargs):
        """
        Initialize this :class:`PyCelery` for use.
        """
        if name is None:
            name = app.config.get('CELERY_TASK_NAME', app.name)
        if config is None:
            config = app.config

        celery = Celery(name)
        celery.config_from_object(config)
        # celery.autodiscover_tasks()
        setattr(self, '_celery', celery)

    @property
    def celery(self):
        """retrieve celery instance"""
        return getattr(self, '_celery')


apps = Celery('task', broker='redis://:syzxss247179876@127.0.0.1:6381/0') # celery application




