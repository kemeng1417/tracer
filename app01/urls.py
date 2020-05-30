from django.conf.urls import url, include
from app01 import views

urlpatterns = [
    url(r'^send/$', views.send),
    url(r'^register/$', views.register, name='register'), # 'app01:register' 反向解析
]