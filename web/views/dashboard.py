import collections
import datetime
import time

from django.http import JsonResponse
from django.shortcuts import render
from web import models
from django.db.models import Count


def dashboard(request, project_id):
    """ 概览 """

    # 问题数据处理
    status_dict = collections.OrderedDict()  # 3.6后为有序字典，之前为无序
    for key, text in models.Issues.status_choices:
        status_dict[key] = {'text': text, 'count': 0}
    issues_data = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']

    # 项目成员
    user_list = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')

    # 最近的十个问题
    top_ten = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[0:10]
    context = {
        'status_dict': status_dict,
        'user_list': user_list,
        'top_ten_object': top_ten,
    }
    return render(request, 'dashboard.html', context)


def issues_chart(request, project_id):
    """ 概览页面生成可视化Highcharts """

    # 最近30天，每天的问题数量
    today = datetime.datetime.now().date()
    data_dict = collections.OrderedDict()
    for i in range(0, 30):
        date = today - datetime.timedelta(days=i)

        data_dict[date.strftime('%Y-%m-%d')] = [time.mktime(date.timetuple()) * 1000, 0]
    result = models.Issues.objects.filter(project_id=project_id,
                                          create_datetime__gte=today - datetime.timedelta(days=30)).extra(
        select={'ctime': 'strftime("%%Y-%%m-%%d", web_issues.create_datetime)'}).values('ctime').annotate(
        ct=Count('id'))
    for item in result:
        data_dict[item['ctime']][1] = item['ct']

    return JsonResponse({'status': True, 'data': list(data_dict.values())})
