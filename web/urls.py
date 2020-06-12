from django.conf.urls import url, include
from web.views import account
from web.views import home

urlpatterns = [
    url(r'^register/$', account.register, name='register'),
    url(r'^login/sms$', account.login_sms, name='login_sms'),
    url(r'^login/$', account.login, name='login'),
    url(r'^logout/$', account.logout, name='logout'),
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    url(r'^img/code/$', account.img_code, name='img_code'),
    url(r'^index/$', home.index, name='index'),
]