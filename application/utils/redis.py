# -*- coding: utf-8 -*-
# @Time  : 2020/12/3 上午9:10
# @Author : 司云中
# @File : redis.py
# @Software: Pycharm
import contextlib
from redis import Redis
import datetime


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

    def record_ip(self, ip):
        """记录IP"""
        with manager_redis() as redis:
            redis.hset(name='ip_record', key=ip, value=datetime.datetime.now().strftime('%Y-%m-%d'))

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

    def get_token_exp(self, id):
        """
        :param id:用户id
        获取token最终失效时间
        数据结构:hash
        """

        with manager_redis() as redis:
            return redis.hget(id, 'refresh_time').decode()

    def save_token_kwargs(self, **kwargs):
        """
        存id号, token, 生成token起始时间,token最终过期时间
        每次检测请求token,看是否需要刷新自动获取

        数据结构:hash
        """
        _copy = kwargs.copy()
        with manager_redis() as redis:
            redis.hset(_copy.pop('id'), mapping=_copy)

    def get_sport_value(self, member, date, type):
        """
        根据name和key获取hash中的用户某一天的步数
        :param member: user.id
        :param date: datetime(string type)
        键:type-member

        数据结构:hash
        """
        with manager_redis() as redis:
            name = self.key(type, member)
            step_count = redis.hget(name, date)
            return int(step_count)

    def set_sport_value(self, member, date, value, type):
        """
        根据name和key以及step_value记录用户某天的运动值
        :param member: user.id
        :param date: datetime(string type)
        :param step_value: step numbers
        键:type-member

        数据结构:hash, sorted set
        """

        with manager_redis() as redis:
            pipe = redis.pipeline()
            name = self.key(type, member)
            result = pipe.hset(name, key=date, value=value)
            self.update_rank_value(pipe, type, date, member, value)  # 更新全服排名
            result = pipe.execute()
            return result

    def update_rank_value(self, pipeline, type, date, member, value):
        """
        用户步数更新时,同步所有人排行榜的运动值
        键:'rank'-type-date

        数据结构:sorted set
        """
        _name = self.key('rank', type, date)
        pipeline.zadd(_name, {member:value})


    def retrieve_step_list(self, member, type, day=None):
        """
        默认获取指定用户过去一周的运动情况
        键:type-member

        数据结构:hash
        """
        day = day or 7
        # 过去时间的元祖,不包含今天
        past = ((datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%d-%m') for i in range(1, day))
        today = datetime.datetime.now().strftime('%Y-%d-%m')
        with manager_redis() as redis:
            name = self.key(type, member)
            result = redis.hmget(name, today, *past)
            print(result)
            return result

    def retrieve_cur_rank(self, type, today):
        """
        当天计数
        获取排名列表前100名,从高到低
        :param type:运动项目类型
        :param today:当天日期
        键:'rank'-type-date

        数据结构:sorted set
        """

        with manager_redis() as redis:
            name = self.key('rank', type, today)
            pipe = redis.pipeline()
            rank_score = pipe.zrevrange(name, 0, 99, withscores=True)  # 前100个成员排名,包含显示分数
            print(rank_score)
            return rank_score

    def retrieve_cur_rank_user(self, type, today, member):
        """
        当天计数
        获取当前用户在全服运动榜中的排名和运动值,从大到小
        :param type:运动项目类型
        :param today:当天日期
        :param member: 用户id
        键:'rank'-type-date

        数据结构:sorted set
        """
        with manager_redis() as redis:
            name = self.key('rank', type, today)
            pipe = redis.pipeline()
            rank = pipe.zrevrank(name, member)  # 获取排名
            score = pipe.zscore(name, member)   # 获取用户的运动值
            result = pipe.execute()
            return result

    def statistic_total_number(self, type, today):
        """
        统计某一类型的运动当天参加的人数

        数据结构:sorted set
        """
        with manager_redis() as redis:
            name = self.key('rank', type, today)
            result = redis.zcard(name)
            print(result)
            return result




@contextlib.contextmanager
def manager_redis(redis_class=BaseRedis, redis=None):
    try:
        redis = redis_class.redis_instance()
        yield redis
    except Exception as e:
        # TODO:redis宕机, 发送邮件到我邮箱
        print(e)
        pass
    finally:
        redis.close()  # 其实可以不要,除非single client connection, 每条执行执行完都会调用conn.release()


@contextlib.contextmanager
def manager_redis_operation(redis_class=BaseRedis):
    try:
        instance = redis_class.redis_operation_instance()
        yield instance
    except Exception as e:
        # TODO:redis宕机, 发送邮件到我邮箱
        print(e)
        pass
