
import json,re,random,time
from requests import request
from loguru import logger
from utils.time_st import UtilTime
from models.cp import Cp,CpTermList,CpTermListHistory
from utils.database.mysql import MysqlPoolSync

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

        self.ut = kwargs.get("ut")
        self.cp = kwargs.get("cp")

    # def Cqssc(self):
    #
    #     """
    #     重庆时时彩
    #     :return:
    #     """
    #
    #     termnumber = 59
    #     name = 'cqssc'
    #
    #     key="term_{}".format(name)
    #
    #     today = self.ut.arrow_to_string(format_v="YYYYMMDD")
    #     tomorrow = self.ut.arrow_to_string(self.ut.today.shift(days=1), format_v="YYYYMMDD")
    #
    #     data = {}
    #     tomorrow_first_next = ""
    #     for i in range(termnumber):
    #
    #         term = "%s0%02d" % (tomorrow, i + 1)
    #
    #         if i == 0:
    #             tomorrow_first_next = term
    #
    #         if i == termnumber - 1:
    #             nextterm = "today"
    #         else:
    #             nextterm = "%s0%02d" % (tomorrow, i + 2)
    #         data[term] = nextterm
    #     self.redis.hset(key, format(tomorrow), json.dumps({"term": data}))
    #
    #     data = {}
    #     for i in range(termnumber):
    #         term = "%s0%02d" % (today, i + 1)
    #         if i == termnumber - 1:
    #             nextterm = tomorrow_first_next
    #         else:
    #             nextterm = "%s0%02d" % (today, i + 2)
    #         data[term] = nextterm
    #     self.redis.hset(key, format(today), json.dumps({"term": data}))

    def getNextTerm(self,term=None):

        # if term:
        #     today = self.ut.arrow_to_string(format_v="YYYYMMDD")
        #     tomorrow = self.ut.arrow_to_string(self.ut.today.shift(days=1), format_v="YYYYMMDD")
        #
        #     autoid = int(term[8:])
        #
        #     if self.cp.termtot == autoid:
        #         tmp = "{}%0{}d".format(tomorrow,len(str(self.cp.termtot)))
        #         return tmp%(1)
        #     else:
        #         tmp = "{}%0{}d".format(today,len(str(self.cp.termtot)))
        #         return tmp%(autoid+1)
        # else:
        today = self.ut.arrow_to_string(format_v="YYYYMMDD")
        if self.cp.opentime == 'all':
            currTime = self.ut.arrow_to_string(format_v="HHmm")
            autoid = (int(currTime[:2]) * 60 + int(currTime[2:])) // self.cp.termnum
            tmp = "{}%0{}d".format(today,len(self.cp.coderule) if self.cp.coderule else len(str(self.cp.termtot)))
            return tmp%(autoid)
        else:
            term = 0
            currterm = None
            currTime = self.ut.arrow_to_string(format_v="HHmm")
            for item in self.cp.opentime.split("|"):
                start_time = item.split('-')[0]
                end_time = item.split('-')[1]

                if currTime < end_time:
                    r = (int(currTime[:2]) * 60 + int(currTime[2:])) - (int(start_time[:2]) * 60 + int(start_time[2:]))
                    if r < 0:
                        currterm = term
                    else:
                        currterm = r // self.cp.termnum + term + 1
                else:
                    a = self.ut.arrow_to_string(
                        self.ut.string_to_arrow(string_s=end_time, format_v="HHmm").shift(hours=-(int(start_time[0:2])),
                                                                                     minutes=-(
                                                                                         int(start_time[2:4]))),
                        "HH:mm")
                    term += (int(a.split(":")[0]) * 60 + int(a.split(":")[1])) // self.cp.termnum + 1

            autoid = currterm
            tmp = "{}%0{}d".format(today,len(self.cp.coderule) if self.cp.coderule else len(str(self.cp.termtot)))
            return tmp%(autoid)


class CpGetHandler(CpTermUpdHandler):
    def __init__(self,**kwargs):
        self.count = 2
        self.cp = kwargs.get('cp',None)
        self.ut = kwargs.get('ut',None)

        super(CpGetHandler,self).__init__(ut=self.ut,cp=self.cp)

    def getRun(self,func):
        """
        官彩,通过爬虫获取开奖号码
        :param func:
        :return: res[0]=>当前期数,res[1]=>当前开奖号码,res=>[2]=>下期期数
        """
        context={}
        exec(func,context)
        res = context["customFuncForCp"]
        return res(request, re, json)

    def getRunCustom(self):
        """
        私彩生成开奖号码
        """

        """
            私彩生成开奖规则通过配置生成执行,暂保留这块逻辑
        """

        rule = json.loads(self.cp.cpnorule)
        cpno = ""
        for item in range(rule['tot']):
            cpno += "{},".format(random.choice(rule['limit']))

        return cpno[:-1]

    def run(self,cpTermListObj):
        #官彩需要爬数据
        if self.cp.type == '0':
            for cpFunc in json.loads(self.cp.code)['code']:
                count  = 0
                while True:
                    count += 1
                    try:
                        res = self.getRun(cpFunc)
                        if cpTermListObj:
                            if res[0] == cpTermListObj.currterm:
                                time.sleep(2)
                                return self.run(cpTermListObj)
                            else:
                                return res
                        else:
                            currterm = self.getNextTerm()
                            print("currterm:{}".format(currterm))
                            if currterm == res[0]:
                                return res
                            else:
                                time.sleep(2)
                                return self.run(cpTermListObj)
                    except Exception as e:
                        print(count,str(e))
                        if count >= self.count:
                            break
                        return self.run(cpTermListObj)
        # 私彩直接生成开奖号码
        else:
            if cpTermListObj:
                currterm = self.getNextTerm(cpTermListObj.currterm)
                nextterm = self.getNextTerm(currterm)
            else:
                currterm = self.getNextTerm()
                nextterm = self.getNextTerm(currterm)

            return currterm,self.getRunCustom(),nextterm


    def save(self):
        try:
            cpTermListObj = CpTermList.get(CpTermList.cpid == self.cp.id)
        except CpTermList.DoesNotExist:
            cpTermListObj = None
        db = MysqlPoolSync().get_conn

        res = self.run(cpTermListObj)

        if not res[0]:
            logger.info("暂未到开奖时间!")
        else:
            if cpTermListObj:
                if cpTermListObj.currterm == res[0]:
                    logger.info("{}[{}]采集数据失败,已采集!".format(self.cp.name, res[0]))
                else:
                    with db.atomic() as transaction:
                        cpTermListObj.cpno = res[1]
                        cpTermListObj.currterm = res[0]
                        cpTermListObj.nextterm = res[2]
                        cpTermListObj.createtime = self.ut.timestamp
                        cpTermListObj.save()
                        CpTermListHistory.create(cpid=self.cp.id, cpno=res[1], term=res[0])
                    logger.info("{}[{}]采集数据成功!".format(self.cp.name, res[0]))
            else:
                with db.atomic() as transaction:
                    CpTermList.create(cpid=self.cp.id,cpno=res[1],currterm=res[0],nextterm=res[2])
                    CpTermListHistory.create(cpid=self.cp.id,cpno=res[1],term=res[0])
                logger.info("{}[{}]采集数据成功!".format(self.cp.name,res[0]))

class CpTaskBase(CpGetHandler):

    def __init__(self,id):

        self.ut = UtilTime()
        self.cp = Cp.get(id=id)

        super(CpTaskBase,self).__init__(cp=self.cp,ut=self.ut)

    def getCp(self):

        self.save()


if __name__ == '__main__':
    cpTask = CpTaskBase(2)

    cpTask.getCp()