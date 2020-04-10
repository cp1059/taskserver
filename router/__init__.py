

api_base_url = "/v1/taskapi"

def join_url(baseurl , url):
    return "{}{}".format(baseurl,url)


from .urls import urlpattern

