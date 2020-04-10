

import json
from apps.base import BaseHandler
from utils.time_st import UtilTime
from utils.decorator.connector import Core_connector

from tasks.task import add_task

class CpTaskInit(BaseHandler):
    @Core_connector(isTransaction=False,isTicket=False,isParams=False)
    async def post(self, *args, **kwargs):

        add_task(self.scheduler)
        return None

class CpTerm(BaseHandler):

    @Core_connector(isTransaction=False,isTicket=False,isParams=False)
    async def post(self, *args, **kwargs):

        # 重庆时时彩
        termnumber = 59
        ut = UtilTime()
        today = ut.arrow_to_string(format_v="YYYYMMDD")
        tomorrow = ut.arrow_to_string(ut.today.shift(days=1), format_v="YYYYMMDD")

        data = {}
        tomorrow_first_next=""
        for i in range(termnumber):

            term = "%s0%02d" % (tomorrow, i + 1)

            if i==0:
                tomorrow_first_next = term

            if i == termnumber - 1:
                nextterm = "today"
            else:
                nextterm = "%s0%02d" % (tomorrow, i + 2)
            data[term] = nextterm
        await self.redis.hset("term_cqssc",format(tomorrow),json.dumps({"term": data}))

        data = {}
        for i in range(termnumber):
            term = "%s0%02d" % (today, i + 1)
            if i == termnumber - 1:
                nextterm = tomorrow_first_next
            else:
                nextterm = "%s0%02d" % (today, i + 2)
            data[term] = nextterm
        await self.redis.hset("term_cqssc",format(today),json.dumps({"term": data}))

        return None