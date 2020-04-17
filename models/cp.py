
from peewee import *
from models.base import BaseModel

class CpTermList(BaseModel):

    id=AutoField(primary_key=True)
    cpid = IntegerField(verbose_name="彩票ID")
    cpno = CharField(verbose_name="开奖号码", max_length=60, default="")
    currterm = CharField(verbose_name="期数", max_length=30, default="")
    nextterm = CharField(verbose_name="下一期数",max_length=30,default="")

    class Meta:
        db_table = 'cptermlist'

class CpTermListHistory(BaseModel):

    id=BigAutoField(primary_key=True)
    cpid = IntegerField(verbose_name="彩票ID")
    cpno = CharField(verbose_name="开奖号码",max_length=60,default="")
    term = CharField(verbose_name="期数", max_length=30, default="")

    class Meta:
        verbose_name = '彩票期数历史明细'
        verbose_name_plural = verbose_name
        db_table = 'cptermlisthistory'


class Cp(BaseModel):

    id=AutoField(primary_key=True)

    name = CharField(max_length=60,verbose_name="彩票名称",default="")
    sort = IntegerField(verbose_name="排序",default=0)

    url = CharField(max_length=255,verbose_name="图片地址")

    cptypeid = CharField(max_length=4,verbose_name="彩票类型",default="")
    typename = CharField(max_length=60,verbose_name="彩票类型名称",default="")

    termnum = IntegerField(verbose_name="多少分钟一期",default=0)

    termtot = IntegerField(verbose_name="总共多少期,这个可以根据开奖时间和多少分钟一期算出来,算头算尾",default=0)

    opentime = CharField(max_length=100,default='0030-0310|0730-2350',verbose_name="每天开奖时间")

    type = CharField(max_length=1,verbose_name="类型,0-官方,1-私有 官方数据需要做采集",default=0)

    status = CharField(max_length=1,verbose_name="状态,0-正常,1-停售,2-维护")

    code = TextField(verbose_name="爬虫代码",default='{"code":[]}')

    coderule = CharField(max_length=20,verbose_name="期号排序规则",default="")

    cpnorule = CharField(max_length=1024,
                                verbose_name="""
                                    开奖号码规则,用在私彩
                                    tot:总共位数,
                                    count:每一位站位多少
                                    limit:号码范围(每一位出奖号码从这里选择)
                                """,
                                default='{"tot":6,"count":1,"limit":[0,1,2,3,4,5,6,7,8,9]}')

    tasktimetable = TextField(verbose_name="任务时间表",default='{"tables":[]}')

    class Meta:
        db_table = 'cp'