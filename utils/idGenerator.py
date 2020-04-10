
from utils.time_st import UtilTime

class idGenerator(object):

    def __init__(self, *args,**kwargs):
        self.redis = kwargs.get("redis")
        self.key = None

    async def userid(self,rolecode):
        self.key = str(rolecode)
        return "%s%08d" % (self.key, await self.redis.incr(self.key))

    async def ordercode(self):
        t = UtilTime().arrow_to_string(format_v="YYYYMMDDHHmmss")
        self.key = t
        res = "TC%s%03d"%(self.key,await self.redis.incr(self.key))
        await self.redis.expire(self.key,10)
        return res

    async def goodscategory(self):
        self.key= "goodscategoryById"
        return "%s%06d" % ("GC", await self.redis.incr(self.key))

    async def goods(self):
        self.key="goodsById"
        return "%s%07d"%("G",await self.redis.incr(self.key))