from django.shortcuts import render
from django.http import JsonResponse
import collections
from web import models
from django.db.models import Count


def statistics(request, project_id):
    """ 统计页面 """
    return render(request, 'statistics.html')


def statistics_priority(request, project_id):
    """ 优先级生成数据"""

    # 找到所有的问题，根据优先级分组后得到每个优先级的数量，构造成highcharts需要的数据
    start = request.GET.get('start')
    end = request.GET.get('end')

    # 构造字典
    data_dict = collections.OrderedDict()
    for key, text in models.Issues.priority_choices:
        data_dict[key] = {'name': text, 'y': 0}

    # 数据库查询所有分组得到的数据
    result = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start,
                                          create_datetime__lt=end).values(
        'priority').annotate(ct=Count('id'))

    for item in result:
        data_dict[item['priority']]['y'] = item['ct']

    return JsonResponse({'status': True, 'data': list(data_dict.values())})


def statistics_project_user(request, project_id):
    """ 项目成员每个人被分配的任务数量及问题类型的配比 """

    # 构造字段
    """
    data_dict = {
        1:{
            name:'xxx',
            status:{
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
            }
        },
        None:{
            name:'xxx2',
            status:{
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
            }
        }    
    }
    """
    # 所有项目的成员及未指派
    # 找到所有的问题，根据优先级分组后得到每个优先级的数量，构造成highcharts需要的数据
    start = request.GET.get('start')
    end = request.GET.get('end')
    all_user_dict = collections.OrderedDict()  # 有序的字典
    all_user_dict[request.tracer.project.creator.id] = {
        'name': request.tracer.project.creator.username,
        'status': {item[0]: 0 for item in models.Issues.status_choices}
    }
    all_user_dict[None] = {
        'name': '未指派',
        'status': {item[0]: 0 for item in models.Issues.status_choices}
    }

    user_list = models.ProjectUser.objects.filter(project_id=project_id)
    for item in user_list:
        all_user_dict[item.user_id] = {
            'name': item.user.username,
            'status': {item[0]: 0 for item in models.Issues.status_choices},
        }

    # 数据库获取相关的所有的问题
    issues = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start,
                                          create_datetime__lt=end)
    for item in issues:
        if not item.assign:
            all_user_dict[None]['status'][item.status] += 1
        else:
            all_user_dict[item.assign_id]['status'][item.status] += 1

    # 获取所有的成员
    categories = [data['name'] for data in all_user_dict.values()]

    data_result_dict = collections.OrderedDict()
    for item in models.Issues.status_choices:
        data_result_dict[item[0]] = {'name': item[1], 'data': []}

    for key, text in models.Issues.status_choices:
        for row in all_user_dict.values():
            count = row['status'][key]
            data_result_dict[key]['data'].append(count)

    context = {
        'status': True,
        'data': {
            'categories': categories,
            'series': list(data_result_dict.values())
        }
    }
    return JsonResponse(context)
