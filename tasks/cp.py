
import json,re,random,time
from requests import request
from bs4 import BeautifulSoup
from loguru import logger
from utils.time_st import UtilTime
from models.cp import Cp,CpTermList,CpTermListHistory
from utils.database import MysqlPool
from asyncio import sleep

"""    
def customFuncForCp(request,re,json):
    headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }
    html = request(method="GET",url="https://www.52cp.cn/cqssc/history",headers=headers,timeout=5).text
    pattern = re.compile(r"myinfo?.*?';")
    res = json.loads(pattern.findall(html)[0].split('=')[1].replace("'","").replace(";",""))
    curterm = res['now']['expect']
    curno = ""
    for item in res['now']['opencode'].split(','):
        curno += str(int(item))
    nextterm = res['next']['expect']
    return curterm,curno,nextterm
    """

class CpTermUpdHandler(object):

    def __init__(self,**kwargs):

        pass

    # def getNextTerm(self,term=None):
    #
    #     # if term:
    #     #     today = self.ut.arrow_to_string(format_v="YYYYMMDD")
    #     #     tomorrow = self.ut.arrow_to_string(self.ut.today.shift(days=1), format_v="YYYYMMDD")
    #     #
    #     #     autoid = int(term[8:])
    #     #
    #     #     if self.cp.termtot == autoid:
    #     #         tmp = "{}%0{}d".format(tomorrow,len(str(self.cp.termtot)))
    #     #         return tmp%(1)
    #     #     else:
    #     #         tmp = "{}%0{}d".format(today,len(str(self.cp.termtot)))
    #     #         return tmp%(autoid+1)
    #     # else:
    #     today = self.ut.arrow_to_string(format_v="YYYYMMDD")
    #     if self.cp.opentime == 'all':
    #         currTime = self.ut.arrow_to_string(format_v="HHmm")
    #         autoid = (int(currTime[:2]) * 60 + int(currTime[2:])) // self.cp.termnum
    #         tmp = "{}%0{}d".format(today,len(self.cp.coderule) if self.cp.coderule else len(str(self.cp.termtot)))
    #         return tmp%(autoid)
    #     else:
    #         term = 0
    #         currterm = None
    #         currTime = self.ut.arrow_to_string(format_v="HHmm")
    #         for item in self.cp.opentime.split("|"):
    #             start_time = item.split('-')[0]
    #             end_time = item.split('-')[1]
    #
    #             if currTime < end_time:
    #                 r = (int(currTime[:2]) * 60 + int(currTime[2:])) - (int(start_time[:2]) * 60 + int(start_time[2:]))
    #                 if r < 0:
    #                     currterm = term
    #                 else:
    #                     currterm = r // self.cp.termnum + term + 1
    #             else:
    #                 a = self.ut.arrow_to_string(
    #                     self.ut.string_to_arrow(string_s=end_time, format_v="HHmm").shift(hours=-(int(start_time[0:2])),
    #                                                                                  minutes=-(
    #                                                                                      int(start_time[2:4]))),
    #                     "HH:mm")
    #                 term += (int(a.split(":")[0]) * 60 + int(a.split(":")[1])) // self.cp.termnum + 1
    #
    #         autoid = currterm
    #         tmp = "{}%0{}d".format(today,len(self.cp.coderule) if self.cp.coderule else len(str(self.cp.termtot)))
    #         return tmp%(autoid)

    def get_cp_term_coderules_before(self):
        coderule = json.loads(self.cp.coderule)
        if coderule['before']['type'] == '0':
            today = self.ut.arrow_to_string(format_v=coderule['before']['value'])
            tomorrow = self.ut.arrow_to_string(self.ut.today.shift(days=1), format_v=coderule['before']['value'])
            return today, tomorrow

    async def getTerm(self,autoid,next_autoid):


        try:
            self.cpTermListObj = await self.db.get(CpTermList, cpid=self.cp.id)
        except CpTermList.DoesNotExist:
            self.cpTermListObj = None

        if self.ispc:
            if self.cpTermListObj:
                self.currterm = self.cpTermListObj.nextterm
            else:
                self.currterm = None
                self.nextterm = None
        else:
            today,tomorrow = self.get_cp_term_coderules_before()
            if autoid>next_autoid:
                self.currterm = "{}{}".format(today,autoid)
                self.nextterm = "{}{}".format(tomorrow,next_autoid)
            else:
                self.currterm = "{}{}".format(today,autoid)
                self.nextterm = "{}{}".format(today, next_autoid)



class CpGetHandler(CpTermUpdHandler):
    def __init__(self,**kwargs):
        self.count = 3

        super(CpGetHandler,self).__init__()

    def getRun(self,func):
        """
        官彩,通过爬虫获取开奖号码
        :param func:
        :return: res[0]=>当前期数,res[1]=>当前开奖号码,res=>[2]=>下期期数
        """
        context={}
        exec(func,context)
        res = context["customFuncForCp"]
        return res(request=request, re=re, json=json,BeautifulSoup=BeautifulSoup,ut=UtilTime)

    # def saveCpTerm(self,today):
    #
    #     tomorrow = self.ut.arrow_to_string(self.ut.today.shift(days=1), format_v="YYYYMMDD")
    #
    #     next = ""
    #     for i in range(self.cp.termtot):
    #         term = "{}%0{}d".format(tomorrow, len(self.cp.coderule) if self.cp.coderule else len(str(self.cp.termtot)))
    #         term = term % (i + 1)
    #         if i == 0:
    #             next = term
    #             break
    #
    #     data = {}
    #     for i in range(self.cp.termtot):
    #
    #         term = "{}%0{}d".format(today, len(self.cp.coderule) if self.cp.coderule else len(str(self.cp.termtot)))
    #         term = term % (i + 1)
    #
    #         if i == self.cp.termtot - 1:
    #             nextterm = next
    #         else:
    #             nextterm = "{}%0{}d".format(today,
    #                                         len(self.cp.coderule) if self.cp.coderule else len(str(self.cp.termtot)))
    #             nextterm = nextterm % (i + 2)
    #         data[term] = nextterm
    #
    #     db = MysqlPoolSync().get_conn
    #     for key in data:
    #         with db.atomic() :
    #             try:
    #                 CpTermListHistory.create(cpid=self.cp.id, cpno="", term=key,nextterm=data[key])
    #             except Exception as e:
    #                 if not ('Duplicate entry' in str(e) and 'cptermlisthistory_ptr_01' in str(e)):
    #                     raise Exception(e)
    #     return None

    def getRunCustom(self):
        """
        私彩生成开奖号码
        """

        """
            私彩生成开奖规则通过配置生成执行,暂保留这块逻辑
        """

        rule = json.loads(self.cp.cpnorule)
        cpno = ""
        for item in range(int(rule['tot'])):
            cpno += "{},".format(random.choice(rule['limit']))

        return cpno[:-1]

    async def run(self):
        #官彩需要爬数据
        if self.cp.type == '0':
            for cpFunc in json.loads(self.cp.code)['code']:
                count  = 0
                timecount = 0
                while True:
                    count += 1
                    try:
                        res = self.getRun(cpFunc)
                        logger.info("{}-{}-{}".format(self.cp.name,self.currterm,res))
                        if res[0] == self.currterm or not self.currterm:
                            return res
                        else:
                            await sleep(5)
                            timecount += 5
                            if timecount >= 5 * 60:
                                break
                            return await self.run()
                    except Exception as e:
                        print(count,str(e))
                        if count >= self.count:
                            break
                        return await self.run()
        # 私彩直接生成开奖号码
        else:
            return self.currterm,self.getRunCustom(),self.nextterm,None

        return None


    async def save(self):

        res = await self.run()

        if not res:
            logger.info("未获取到该开奖信息!")
            return None

        cpTermListObj = self.cpTermListObj

        if not res[0]:
            logger.info("暂未到开奖时间!")
        else:
            async with MysqlPool().get_conn.atomic_async():
                if cpTermListObj:
                    if cpTermListObj.currterm == res[0]:
                        logger.info("{}[{}]采集数据失败,已采集!".format(self.cp.name, res[0]))
                    else:
                        cpTermListObj.cpno = res[1]
                        cpTermListObj.currterm = res[0]
                        cpTermListObj.nextterm = res[2]
                        cpTermListObj.createtime = self.ut.timestamp
                        cpTermListObj.nexttime = res[3] if len(res)>3 else 0
                        await self.db.update(cpTermListObj)
                else:
                        await self.db.create(
                            CpTermList,
                            cpid=self.cp.id,
                            cpno=res[1],
                            currterm=res[0],
                            nextterm=res[2],
                            createtime=self.ut.timestamp,
                            nexttime = res[3] if len(res)>3 else 0)

                await self.db.create(CpTermListHistory,cpid=self.cp.id, cpno=res[1], term=res[0],createtime=self.ut.timestamp)

                logger.info("{}[{}-{}-{}]采集数据成功!".format(self.cp.name, res[0],res[1],res[2]))

class CpTaskBase(CpGetHandler):

    def __init__(self,id,db):

        self.pk = id
        self.db = db
        super(CpTaskBase,self).__init__()

    async def getCp(self,**kwargs):

        self.cp = await self.db.get(Cp, id=self.pk)

        self.ut = UtilTime()
        self.ispc = kwargs.get("ispc",None)

        await self.getTerm(kwargs.get("autoid",None),kwargs.get("next_autoid",None))
        await self.save()

if __name__ == '__main__':
    cpTask = CpTaskBase(4)

    print(cpTask.getNextTerm())