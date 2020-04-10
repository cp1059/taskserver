
import json

class RedisBase(object):

    def __init__(self,**kwargs):
        self.redis = kwargs.get("redis")
        self.key = str(kwargs.get("key",None))

    async def set_dict(self,value):
        await self.redis.set(self.key,json.dumps(value))

    async def get_dict(self):
        res = await self.redis.get(self.key)
        return json.loads(res) if res else res

    async def del_dict(self):
        await self.redis.delete(self.key)

    async def set_hash(self, dictKey, value):
        await self.redis.hset(self.key, dictKey, json.dumps(value))

    async def get_hash(self, dictKey):
        res = await self.redis.hget(self.key, dictKey)
        return json.loads(res) if res else res

    async def del_hash(self, dictKey):
        await self.redis.hdel(self.key, dictKey)

    async def delall_hash(self):
        await self.redis.delete(self.key)

    async def getall_hash(self):

        res = await self.redis.hgetall(self.key)
        res_ex = []
        if res:
            for key in res:
                res_ex.append(json.loads(res[key]))
        return res_ex if res else None

    async def save(self,**kwargs):
        key = kwargs.get("key")
        value = kwargs.get("value")
        await self.set_hash(key,value)

    async def save_ex(self,**kwargs):
        downtable = kwargs.get("downtable")
        downkey = kwargs.get("downkey")
        downvalue = kwargs.get("downvalue")

        key = kwargs.get("key")
        res = await self.get_hash(key)
        if downtable not in res:
            res[downtable] = dict()

        res[downtable][downkey] = downvalue
        await self.set_hash(key,res)

    async def delete_ex(self,**kwargs):
        downtable = kwargs.get("downtable")
        downkey = kwargs.get("downkey")

        key = kwargs.get("key")
        res = await self.get_hash(key)
        res[downtable].pop(downkey)
        await self.set_hash(key,res)

    async def delete(self,**kwargs):
        key = kwargs.get("key")
        await self.del_hash(key)

    async def filter(self,**kwargs):

        pk = kwargs.get("pk",None)
        filter_value = kwargs.get('filter_value') if kwargs.get('filter_value') else {}

        res=[]
        if pk:
            res.append(await self.get_hash(pk))
        else:
            res = await self.getall_hash()

        data=[]
        if res:
            for resValue in res:
                isOk = True

                #其他查询字段
                for item in filter_value:
                    rValue = filter_value.get(item,None)
                    if rValue and item in resValue and str(rValue) != str(resValue.get(item)) :
                        isOk = False
                        break
                if not isOk:
                    continue

                data.append(resValue)

        if pk:
            return data[0] if len(data) else {}
        else:
            data.sort(key=lambda k: (k.get('createtime', 0)), reverse=True)
            return data