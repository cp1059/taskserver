
from peewee import *

from utils.time_st import MyTime
from utils.database.mysql import MysqlPoolSync

class BaseModel(Model):

    createtime = BigIntegerField(default=MyTime().timestamp, verbose_name="创建时间")

    def save(self, *args, **kwargs):

        if not self.createtime:
            self.createtime = MyTime().timestamp

        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        # table_name = 'users'
        database = MysqlPoolSync().get_conn
        legacy_table_names = False
