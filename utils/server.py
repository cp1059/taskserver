import asyncio
import tornado.web
import tornado.ioloop

from tornado.options import options

from apscheduler.schedulers.tornado import TornadoScheduler

from utils.database import MysqlPool
from loguru import logger
from router import urlpattern
from config import common

from tasks.task import add_task

class Server(object):

    def __init__(self):
        self.scheduler = ""

    def make_app(self,loop):
        """
        加载app
        :param loop:
        :return:
        """
        #初始化日志管理

        logger.add("logs/api.log",rotation="00:00:01",retention='10 days',enqueue=True,encoding='utf-8',backtrace=True, diagnose=True)

        #初始化web application
        apps = tornado.web.Application(handlers=urlpattern,default_host=None,transforms=None,**common)

        #初始化redis
        # apps.redis = RedisPoolSync().get_conn()

        #初始化mysql
        apps.mysql = MysqlPool().get_manager

        return apps

    def init_scheduler(self,db):
        self.scheduler = TornadoScheduler()
        self.scheduler.start()

        add_task(self.scheduler,db)

    def start(self):
        try:
            logger.info("server start...")

            loop = asyncio.get_event_loop()
            app = self.make_app(loop)

            self.init_scheduler(app.mysql)

            app.listen(options.common_port)
            logger.info("port: {}".format(options.common_port))
            loop.run_forever()
        except KeyboardInterrupt:
            logger.info("server stop")