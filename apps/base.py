
from tornado.web import RequestHandler
from aioredis import Redis

from services.cache.base import RedisBase
from utils.idGenerator import idGenerator


class BaseHandler(RequestHandler):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, PATCH, OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Authorization,Access-Control-Allow-Origin, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')

    def options(self, *args, **kwargs):
        pass

    # @property
    # def scheduler(self):
    #     return self.application.scheduler

    @property
    def db(self):
        """
        mysql操作对象
        :return:
        """
        return self.application.mysql

    @property
    def redis(self) -> Redis:
        """
        redis操作对象
        :return:
        """
        return self.application.redis

    def redisC(self,key):
        """
        redis操作集合
        :param key:
        :return:
        """
        return RedisBase(redis=self.redis,key=key)

    def idGeneratorClass(self):
        """
        id生成器
        :return:
        """
        return idGenerator(redis=self.redis)
