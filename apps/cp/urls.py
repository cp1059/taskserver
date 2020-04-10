from tornado.web import url
from apps.cp.api import *
from router import api_base_url,join_url

api_url = join_url(api_base_url,"/cp")

urlpattern = [
    url(join_url(api_url, '/cpinit'), CpTaskInit),
    url(join_url(api_url, '/term'), CpTerm),
]

print(api_url)