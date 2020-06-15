from django.conf.urls import url, include
from web.views import account
from web.views import home
from web.views import project
from web.views import manage
from web.views import wiki

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

    # 进入项目管理,可以采用include简化路由
    url(r'^manage/(?P<project_id>\d+)/', include([
        url(r'^dashboard/$', manage.dashboard, name='dashboard'),
        url(r'^issues/$', manage.issues, name='issues'),
        url(r'^statistics/$', manage.statistics, name='statistics'),
        url(r'^file/$', manage.file, name='file'),

        url(r'^wiki/$', wiki.wiki, name='wiki'),
        url(r'^wiki/add/$', wiki.wiki_add, name='wiki_add'),
        url(r'^wiki/delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name='wiki_delete'),
        url(r'^wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
        url(r'^wiki/catalog/$', wiki.wiki_catalog, name='wiki_catalog'),

        url(r'^setting/$', manage.setting, name='setting'),

    ],None,None)),
]
"""
url(r'^manage/(?P<project_id>\d+)/dashboard/$', project.project_unstar, name='project_unstar'),
url(r'^manage/(?P<project_id>\d+)/issues/$', project.project_unstar, name='project_unstar'),
url(r'^manage/(?P<project_id>\d+)/statistics/$', project.project_unstar, name='project_unstar'),
url(r'^manage/(?P<project_id>\d+)/file/$', project.project_unstar, name='project_unstar'),

url(r'^manage/(?P<project_id>\d+)/wiki/$', project.project_unstar, name='project_unstar'),
url(r'^manage/(?P<project_id>\d+)/setting/$', project.project_unstar, name='project_unstar'),
"""
