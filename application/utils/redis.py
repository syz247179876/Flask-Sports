# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 上午9:10
# @Author : 司云中
# @File : redis.py
# @Software: Pycharm
import contextlib
from rediscluster import RedisCluster
from redis import Redis


class BaseRedis:
    _instance = {}
    _redis_instances = {}

    def __init__(self, db, redis):
        self.db = db  # 选择配置中哪一种的数据库
        self.__redis = redis

    @classmethod
    def init_app(cls, app):
        return cls.choice_redis_db(app)

    @classmethod
    def choice_redis_db(cls, app):
        """
        选择配置中指定的数据库
        单例模式，减小new实例的大量创建的次数，减少内存等资源的消耗（打开和关闭连接），共享同一个资源
        """

        if not cls._instance.setdefault(cls.__name__, None):
            db = app.config.get('CACHE_NAME')
            # cls._redis_instances[db] = RedisCluster(startup_nodes=app.config.get('STARTUP_NODES'),
            #                                         decode_responses=True)  # redis集群(一主三从)
            cls._redis_instances[db] = Redis(**app.config.get('REDIS_DB_URL'), decode_responses=True)
            cls._instance[cls.__name__] = cls(db, cls._redis_instances[db])  # 自定义操作类实例
        return cls._instance[cls.__name__]

    @property
    def redis(self):
        return self.__redis

    @redis.setter
    def redis(self, value):
        self.__redis = value

    @classmethod
    def redis_instance(cls):
        """获取存放单例字典中的实例的redis属性"""
        return cls._instance[cls.__name__].redis

    @classmethod
    def redis_operation_instance(cls):
        """获取当前操作类(BaseRedis)的实例"""
        return cls._instance[cls.__name__]


    @staticmethod
    def key(*args):
        """
        字符串拼接形成key
        :param args: 元祖依赖值
        :return: str
        """
        keywords = (str(value) if not isinstance(value, str) else value for value in args)
        # return make_password('-'.join(keywords), salt=self.salt)   # 加密贼耗时
        return '-'.join(keywords)

    def check_code(self, key, value):
        """
        检查value是否和redis中key映射的value对应？
        :param key: key in key
        :param value: value from outside
        :return: bool
        """
        with manager_redis() as redis:
            if redis is None:
                return False
            elif redis.exists(key):
                _value = redis.get(key).decode()
                return True if _value == value else False
            else:
                return False

    def save_code(self, key, code, time):
        """
        缓存验证码并存活 time（s）
        :param key: key of redis
        :param code: code from outside
        :param time: (second)
        :return: bool
        """

        with manager_redis() as redis:
            if redis is None:
                return False
            redis.setex(key, time, code)  # 原子操作，设置键和存活时间

    def get_ttl(self, key):
        """
        获取某个键的剩余过期时间
        键永久：-1
        键不存在：-2
        :param key: key of redis
        :return: int
        """
        with manager_redis() as redis:
            if redis is None:
                return False
            redis.ttl(key)

    @staticmethod
    def get_client_ip(request):

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 真实IP
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')  # 代理IP,如果没有代理,也是真实IP
        return ip


@contextlib.contextmanager
def manager_redis(redis_class=BaseRedis, redis=None):
    try:
        redis = redis_class.redis_instance()
        yield redis
    except Exception as e:
        print(e)
    finally:
        redis.close()  # 其实可以不要,除非single client connection, 每条执行执行完都会调用conn.release()

@contextlib.contextmanager
def manager_redis_operation(redis_class=BaseRedis):
    try:
        instance = redis_class.redis_operation_instance()
        yield instance
    except Exception as e:
        print(e)