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
                                          create_datetime__lte=end).values(
        'priority').annotate(ct=Count('id'))
    print(result)
    for item in result:
        data_dict[item['priority']]['y'] = item['ct']

    return JsonResponse({'status': True, 'data': list(data_dict.values())})


def statistics_project_user(request, project_id):
    """ 项目成员每个人被分配的任务数量及问题类型的配比 """




    context = {
        'status': True,
        'data': {
            'categories': [],
            'series': [
                {
                    'name': '新建',
                    'data': [5, 4, 3],
                }
            ]
        }
    }
    return JsonResponse({'status': True, 'data':})
