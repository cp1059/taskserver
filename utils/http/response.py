
import json

code = {
    'success': '10000',
    'error': '10001'
}
res = {
    'msg': '',
    'data': '',
    'code': code['success'],
}

def HttpResponse(self=None,success=True,data=None,rescode=code['success'],msg='',headers=None):
    # if self.status_code != 200:
    #     success = False

    if rescode != code['success']:
        res['code'] = rescode
        res['msg'] = msg if msg else '请求出错,请稍后再试！'
    else:
        if success:
            res['code'] = code['success']
            res['msg'] = msg if msg else '操作成功'
        else:
            res['code'] = code['error']
            res['msg'] = msg if msg else '请求出错,请稍后再试！'
    res['data'] = data
    return json.dumps(res)