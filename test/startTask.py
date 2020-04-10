
from requests import request


url="http://localhost:8888/v1/taskapi/cp/cpinit"


res = request(method="POST",url=url)

print(res.content)