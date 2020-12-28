# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 上午9:10
# @Author : 司云中
# @File : redis.py
# @Software: Pycharm
import contextlib
import datetime
import time

from flask import current_app
from redis import Redis, RedisError


class BaseRedis:
    _instance = {}  # 用于子类继承共用父类的类属性
    _redis_instances = {}

    def __init__(self, db, redis):
        self.db = db  # 选择配置中哪一种的数据库
        self.__redis = redis

    @classmethod
    def init_app(cls, app):
        return cls._load_config_redis(app)

    # @classmethod
    # def choice_redis_db(cls, app):
    #     """
    #     选择配置中指定的数据库
    #     单例模式，减小new实例的大量创建的次数，减少内存等资源的消耗（打开和关闭连接），共享同一个资源
    #     """
    #
    #     if not cls._instance.setdefault(cls.__name__, None):
    #         db = app.config.get('CACHE_NAME')
    #         # cls._redis_instances[db] = RedisCluster(startup_nodes=app.config.get('STARTUP_NODES'),
    #         #                                         decode_responses=True)  # redis集群(一主三从)
    #         cls._redis_instances[db] = Redis(**app.config.get('REDIS_DB_URL'), decode_responses=True)
    #         cls._instance[cls.__name__] = cls(db, cls._redis_instances[db])  # 自定义操作类实例
    #     return cls._instance[cls.__name__]

    @classmethod
    def _load_config_redis(cls, app):
        """
        加载配置中的缓存数据库
        单例模式，减小new实例的大量创建的次数，减少内存等资源的消耗（打开和关闭连接），共享同一个资源
        """
        if not cls._instance.setdefault(cls.__name__, None):
            db = app.config.get('REDIS_DB')

            assert 'default' in db, " 'default' config should be declared in CACHES attribute"

            for name, config in db.items():
                cls._redis_instances[name] = Redis(**config)
            cls._instance[cls.__name__] = cls(db, cls._redis_instances.get('default'))  # 默认配置default
        return cls._instance[cls.__name__]

    @property
    def redis(self):
        """default redis"""
        return self.__redis

    @redis.setter
    def redis(self, value):
        self.__redis = value

    @classmethod
    def redis_instance(cls, redis_name):
        """获取存放单例字典中的redis实例"""
        return cls._redis_instances[redis_name]

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
        return '-'.join(keywords)

    @staticmethod
    def check_code(key, value, redis_name='default'):
        """
        检查value是否和redis中key映射的value对应

        :param redis_name: redis name in config
        :param key: key in key
        :param value: value from outside
        :return: bool
        """
        with manager_redis(redis_name) as redis:
            if redis is None:
                return False
            elif redis.exists(key):
                _value = redis.get(key).decode()
                return True if _value == value else False
            else:
                return False

    @staticmethod
    def save_code(key, code, time, redis_name='default'):
        """
        缓存验证码并存活 time（s）

        :param redis_name: redis name in config
        :param key: key of redis
        :param code: code from outside
        :param time: (second)
        :return: bool
        """

        with manager_redis(redis_name) as redis:
            if redis is None:
                return False
            redis.setex(key, time, code)  # 原子操作，设置键和存活时间

    @staticmethod
    def get_ttl(key, redis_name='default'):
        """
        获取某个键的剩余过期时间
        键永久：-1
        键不存在：-2

        :param redis_name: redis name in config
        :param key: key of redis
        :return: int
        """
        with manager_redis(redis_name) as redis:
            if redis is None:
                return False
            redis.ttl(key)

    @staticmethod
    def get_token_exp(identity, redis_name='default'):
        """
        获取token最终失效时间

        :param redis_name: redis name in config
        :param identity:用户id

        数据结构:hash
        """

        with manager_redis(redis_name) as redis:
            return redis.hget(identity, 'refresh_time').decode()

    @staticmethod
    def save_token_kwargs(redis_name, **kwargs):
        """
        存id号, token, 生成token起始时间,token最终过期时间
        每次检测请求token,看是否需要刷新自动获取

        数据结构:hash
        """

        _copy = kwargs.copy()
        with manager_redis(redis_name) as redis:
            redis.hset(_copy.pop('id'), mapping=_copy)

    def save_ident(self, phone, ip, redis_name='default'):
        """
        保存唯一身份凭证

        数据结构:hash table
        """
        with manager_redis(redis_name) as redis:
            redis.hset('identity', phone, ip)

    def get_sport_value(self, member, date, mold, redis_name='default'):
        """
        根据name和date获取hash中的用户某一天的步数

        :param redis_name: redis name in config
        :param mold: 运动类型
        :param member: user.id
        :param date: datetime(string mold)

        键:mold-date
        值:{member:value}

        数据结构:hash
        """
        member = str(member)  # 用户id
        with manager_redis(redis_name) as redis:
            name = self.key(mold, date)
            step_count = redis.hget(name, member)
            return step_count

    def set_sport_value(self, member, date, value, mold, redis_name='default'):
        """
        根据mold和date以及value记录用户某天的运动值

        :param redis_name: redis name in config
        :param mold: 运动类型
        :param value: 运动值
        :param member: user.id
        :param date: datetime(string mold)

        键:mold-date
        值:{member:value}

        数据结构:hash, sorted set
        """
        member = str(member)
        with manager_redis(redis_name) as redis:
            pipe = redis.pipeline()
            name_time = self.key(mold, date)
            pipe.hset(name_time, key=member, value=value)  # 设置以时间为轴的hash
            name_user = self.key(mold, member)
            pipe.hset(name_user, key=date, value=value)  # 以用户为轴的hash
            pipe.execute()

    def update_whole_rank(self, member, date, value, mold, redis_name='default'):
        """
        用户步数更新时,同步所有人排行榜的运动值

        键:-mold-date
        值:{member:port}

        数据结构:sorted set
        """
        member = str(member)
        with manager_redis(redis_name) as redis:
            name = self.key('rank', mold, date)
            redis.zadd(name, {member: value})

    def retrieve_step_list(self, member, mold, day=None, redis_name=None):
        """
        默认获取指定用户过去一周的运动情况

        键:mold-member

        数据结构:hash
        """
        member = str(member)
        day = day or 7
        # 过去时间的元祖,不包含今天
        past = ((datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%d-%m') for i in range(1, day))
        today = datetime.datetime.now().strftime('%Y-%d-%m')
        with manager_redis(redis_name) as redis:
            name = self.key(mold, member)
            result = redis.hmget(name, today, *past)
            return result

    def retrieve_cur_rank(self, mold, today=None, redis_name='default'):
        """
        当天计数,获取排名列表前100名,从高到低

        :param redis_name: redis name in config
        :param mold:运动项目类型
        :param today:当天日期

        键:'rank'-mold-date

        数据结构:sorted set
        """
        today = today or (datetime.datetime.now()).strftime('%Y-%m-%d')
        with manager_redis(redis_name) as redis:
            name = self.key('rank', mold, today)
            rank_score = redis.zrevrange(name, 0, 99, withscores=True)  # 前100个成员排名,包含显示分数
            return rank_score

    def retrieve_cur_rank_user(self, member, mold, today=None, redis_name='default'):
        """
        当天计数,获取当前用户在全服运动榜中的排名和运动值,从大到小

        :param redis_name: redis name in config
        :param mold:运动项目类型
        :param today:当天日期
        :param member: 用户id
        :return [rank ,score]

        键:'rank'-mold-date

        数据结构:sorted set
        """
        member = str(member)
        today = today or (datetime.datetime.now()).strftime('%Y-%m-%d')
        with manager_redis(redis_name) as redis:
            name = self.key('rank', mold, today)
            pipe = redis.pipeline()
            pipe.zrevrank(name, member)  # 获取当前用户的排名
            pipe.zscore(name, member)  # 获取当前用户的运动值
            result = pipe.execute()
            return result

    def statistic_total_number(self, mold, today, redis_name='default'):
        """
        统计某一类型的运动当天参加的人数

        数据结构:sorted set
        """

        with manager_redis(redis_name) as redis:
            name = self.key('rank', mold, today)
            result = redis.zcard(name)
            return result

    def rewrite_data_to_mongo(self, mold, date=None, redis_name='default'):
        """
        将以时间为轴的所有用户当天数据写回mongodb

        :return {member:value}
        """
        today = date or (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        with manager_redis(redis_name) as redis:
            name = self.key(mold, today)
            result_dict = redis.hgetall(name)
            return result_dict


class SportRedis(BaseRedis):
    """与运动相关redis业务处理"""
    pass


class RateRedis(BaseRedis):
    """用户行为redis业务处理"""

    db_name = 'rate'

    @classmethod
    def _choice_redis_db(cls, app):
        """
        选择配置中指定的数据库
        单例模式，减小new实例的大量创建的次数，减少内存等资源的消耗（打开和关闭连接），共享同一个资源
        """

        if not cls._instance.setdefault(cls.__name__, None):
            db = app.config.get('REDIS_DB')
            if not cls._redis_instances[cls.db_name]:
                cls._redis_instances[cls.db_name] = Redis(**db[cls.db_name], decode_responses=True)
            cls._instance[cls.__name__] = cls(db, cls._redis_instances[cls.db_name])  # 自定义操作类实例
        return cls._instance[cls.__name__]

    def record_ip(self, ip, path, redis_name='default'):
        """
        记录IP
        键:ip
        值:path

        限流思想:
        1.采用Hash+List进行存储,一个用户一个Hash
        2.先检查当前key下用户的列表中是否超出限流长度,如果没有,执行第3步;否则执行第4步
        3.将path追加到list末尾
        4.清除list中已经不再被限流的path,


        数据结构: List + Hash
        """
        with manager_rate_redis() as redis:
            redis.hset(name='ip_record', key=ip, value=datetime.datetime.now().strftime('%Y-%m-%d'))

            key = self.key(ip)
            redis.rpush(key, path)

    def check_throttling(self, key, timer, duration, num_requests):
        """
        检查是否满足限流
        使用deque替代list
        """
        from collections import deque

        with manager_rate_redis() as redis:
            history = redis.get(key, deque())
            now = timer()

            # 如果此时history中存在已经不满足限流的记录,则删去
            while history and history[-1] <= now - duration:
                history.pop()
            if len(history) >= num_requests:
                return False, None  # 次数仍然达到限流阀值
            return True, history  # 可以访问

    def record_throttle(self, key, history, duration):
        """向name为key的history队列中添加当前的请求时间戳"""
        history.appendleft(key, history)

        with manager_rate_redis() as redis:
            redis.set(self.key, history, duration)


@contextlib.contextmanager
def manager_redis(redis_name=None, redis_class=BaseRedis):
    redis = None
    redis_name = redis_name or 'default'
    try:
        redis = redis_class.redis_instance(redis_name)
        yield redis  # 如有异常,回退到此,抛出异常
    except RedisError as e:
        print(f'redis出现异常:{e}')
    finally:
        redis.close()  # 其实可以不要,除非single client connection, 每条执行执行完都会调用conn.release()


@contextlib.contextmanager
def manager_base_package(redis_class=BaseRedis):
    try:
        instance = redis_class.redis_operation_instance()
        yield instance
    except RedisError as e:
        print(f'redis执行错误:{e}')


@contextlib.contextmanager
def manager_rate_redis():
    redis_name = 'rate'
    redis_class = RateRedis
    redis = None
    try:
        redis = redis_class.redis_instance(redis_name)
        yield redis
    except RedisError as e:
        print(f'redis出现异常:{e}')
    finally:
        redis.close()


@contextlib.contextmanager
def manager_rate_package():
    redis_class = RateRedis
    try:
        instance = redis_class.redis_operation_instance()
        yield instance
    except RedisError as e:
        print(f'redis执行错误:{e}')


class DefaultCacheRedisProxy(object):
    """
    Proxy access to the default Cache(Redis) object's attributes
    """

    def __getattr__(self, name):
        return BaseRedis.redis_instance(name)


cache_redis = DefaultCacheRedisProxy()
