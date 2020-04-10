
import json
from functools import wraps
from loguru import logger
from utils.exceptions import PubErrorCustom,InnerErrorCustom
from utils.http.response import HttpResponse
from utils.aes import decrypt,encrypt
from utils.database import MysqlPool

# import tornado.httputil.HttPHeaders

class Core_connector:

    def __init__(self,**kwargs):

        #是否加数据库事务
        self.isTransaction = kwargs.get('isTransaction',True)

        #是否加密
        self.isPasswd = kwargs.get('isPasswd', False)

        #是否校验ticket
        self.isTicket = kwargs.get('isTicket', True)

        #是否获取参数
        self.isParams = kwargs.get('isParams',True)

    async def __request_validate(self,outside_self,**kwargs):

        #校验凭证并获取用户数据
        if self.isTicket:
            token = outside_self.request.headers.get_list("Authorization")
            if len(token)<=0:
                raise InnerErrorCustom(code="20001", msg="拒绝访问!")
            else:
                token = token[0]
            c = outside_self.redisC(key=token)
            result = await c.get_dict()
            if not result:
                raise InnerErrorCustom(code="20002",msg="拒绝访问")

            if result.get("status") == '1':
                raise PubErrorCustom("账户已到期!")
            elif result.get("status") == '2':
                raise PubErrorCustom("账户已冻结!")
            outside_self.user = result
            outside_self.token = token

        outside_self.data = None

        if self.isParams:
            if outside_self.request.method in ['POST','PUT']:
                outside_self.data = outside_self.get_body_argument("data",None)
                if not outside_self.data:
                    outside_self.data = json.dumps(json.loads(outside_self.request.body.decode('utf-8')).get("data",None)) if outside_self.request.body \
                        else '{}'
                if not outside_self.data:
                    outside_self.data='{}'
            elif outside_self.request.method == 'GET':
                outside_self.data = outside_self.get_argument("data",None)
            elif outside_self.request.method == 'DELETE':
                outside_self.data='{}'
            else:
                raise PubErrorCustom("拒绝访问!")

            if not outside_self.data:
                raise PubErrorCustom("拒绝访问!")

            if self.isPasswd:
                if outside_self.data != '{}':
                    outside_self.data = json.loads(decrypt(outside_self.data))
                else:
                    outside_self.data = json.loads(outside_self.data)
            else:
                outside_self.data = json.loads(outside_self.data)


        logger.info("请求的参数: {}".format(outside_self.data))

    async def __run(self, func, outside_self, *args, **kwargs):

        if self.isTransaction:
            async with MysqlPool().get_conn.atomic_async():
                res = await func(outside_self, *args, **kwargs)
        else:
            res = await func(outside_self, *args, **kwargs)

        if not isinstance(res, dict):
            res = {'data': None, 'msg': None, 'header': None}
        if 'data' not in res:
            res['data'] = None
        if 'msg' not in res:
            res['msg'] = {}
        if 'header' not in res:
            res['header'] = None

        logger.info("返回的参数: {}".format(res['data']))
        if self.isPasswd and res['data']:
            res['data'] = encrypt(json.dumps(res['data'])).decode('ascii')

        # if 'caches' in res and res['caches']:
        #     c = outside_self.redisC(key=None)
        #     for item in res['caches']:
        #         c.key = item['table']
        #         if item['method'] == 'save':
        #             await c.save(**item)
        #         elif item['method'] == 'delete':
        #             await c.delete(**item)
        #         elif item['method'] == 'save_ex':
        #             await c.save_ex(**item)

        return HttpResponse(self=outside_self,data=res['data'], headers=res['header'], msg=res['msg'])

    def __response__validate(self, outside_self, func):

        pass

    def __call__(self,func):
        @wraps(func)
        async def wrapper(outside_self,*args, **kwargs):
            try:
                await self.__request_validate(outside_self,**kwargs)
                response = await self.__run(func,outside_self,*args, **kwargs)
                self.__response__validate(outside_self,func)

                outside_self.finish(response)
            except PubErrorCustom as e:
                outside_self.finish(HttpResponse(success=False, msg=e.msg, data=None))
                logger.opt(lazy=True,exception=True).error(e.msg)
            except InnerErrorCustom as e:
                outside_self.finish(HttpResponse(success=False, msg=e.msg, data=None,rescode=e.code))
                logger.exception(e.msg)
            except Exception as e:
                outside_self.finish(HttpResponse(success=False, msg=str(e), data=None))
                logger.exception("err")

        return wrapper