from django.conf.urls import url, include
from web.views import account
from web.views import home
from web.views import project


urlpatterns = [
    url(r'^register/$', account.register, name='register'),
    url(r'^login/sms$', account.login_sms, name='login_sms'),
    url(r'^login/$', account.login, name='login'),
    url(r'^logout/$', account.logout, name='logout'),
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    url(r'^img/code/$', account.img_code, name='img_code'),
    url(r'^index/$', home.index, name='index'),

    # 项目管理
    url(r'^project/list/$', project.project_list, name='project_list'),
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar, name='project_unstar'),
]
