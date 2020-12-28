# -*- coding: utf-8 -*-
# @Time  : 2020/12/28 下午8:57
# @Author : 司云中
# @File : throttle.py
# @Software: Pycharm
import time

from flask import request as req, current_app

from application.utils.exception import ImproperlyConfigured, ThrottleException
from extensions.redis import cache_redis, manager_rate_package


class BaseApiThrottle(object):
    """全局API限流"""

    def allow_request(self, view):
        """
        Return `True` if the request should be allowed, `False` otherwise.
        """
        raise NotImplementedError('.allow_request() must be overridden')

    def get_ident(self):
        """
        Identify the machine making the request
        by parsing HTTP_X_FORWARDED_FOR
        """
        addr = req.access_route
        return addr[-1]

    def wait(self):
        """
        Optionally, return a recommended number of seconds to wait before
        the next request.
        """
        return None


class SimpleRateThrottle(BaseApiThrottle):

    """
    选用redis作为默认的cache
    针对具体的某个scope进行限流,用于视图类中使用
    """
    cache = cache_redis
    timer = time.time
    cache_format = 'throttle_%(scope)s_%(ident)s'
    scope = None
    THROTTLE_RATES = current_app.config.get('DEFAULT_THROTTLE_RATE')

    def __init__(self):
        if not getattr(self, 'rate', None):
            self.rate = self.get_rate() # 获取限流频率
        self.num_requests, self.duration = self.parse_rate(self.rate)

    def get_cache_key(self, req):
        """
        Should return a unique cache-key which can be used for throttling.
        Must be overridden.

        May return `None` if the request should not be throttled.
        """
        raise NotImplementedError('.get_cache_key() must be overridden')

    def get_rate(self):
        """
        根据scope从配置文件中获取限流频率
        {'user-praise': '1000000/day',}
        """
        if not getattr(self, 'scope', None):
            msg = ("You must set either `.scope` or `.rate` for '%s' throttle" %
                   self.__class__.__name__)
            raise ImproperlyConfigured(msg)

        try:
            return self.THROTTLE_RATES[self.scope]
        except KeyError:
            msg = "No default throttle rate set for '%s' scope" % self.scope
            raise ImproperlyConfigured(msg)

    def parse_rate(self, rate):
        """
        解析配置文件中形如'1000000/day'的限流频率

        :return: (1000000, 86400)
        """
        if rate is None:
            return (None, None)  # 此时并未设置任何限流类
        num, period = rate.split('/')  # 用'/'区分次数和时间间隔
        num_requests = int(num)
        duration = {'s':1, 'm':60, 'h':3600, 'd':86400}[period[0]] # 不同的字母代表不同的时常
        return (num_requests, duration)


    def allow_request(self, view):
        """
        检查某线程执行该视图是否为限流了

        :return:
        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        if self.rate is None: # 若如限流
            return True
        self.key = self.get_cache_key(req)
        if self.key is None:  # 若未设置key,默认无限流
            return True

        with manager_rate_package() as manager:

            is_throttle, history = manager.check_throttling(self.key, self.timer, self.duration, self.num_requests) # 检查是否未被限流
            return self.throttle_success(history) if is_throttle else self.throttle_failure()

    def throttle_success(self, history):
        """未限流"""
        with manager_rate_package() as manager:
            manager.record_throttle(self.key, history, self.duration)  # 增加一次限流次数
        return True

    def throttle_failure(self):
        """429 code"""
        raise ThrottleException()
