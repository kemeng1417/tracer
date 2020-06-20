from django.shortcuts import render, redirect
from web.forms.project import ProjectModelForm
from django.http import JsonResponse, HttpResponse
from web import models
from utils.tencent.cos import create_bucket
import time


def project_list(request):
    """项目列表"""
    if request.method == 'GET':
        # get 请求查看项目列表
        """
            1.从数据库中获取三部分的数据
	            我创建的项目：已星标、未星标
	            我参与的所有项目：已星标、未星标
            2.提取已星标
 	        列表= 循环我创建的+我参与的，把所有星标的项目提取出来
            得到三个列表：星标，创建，参与	
        """
        project_dict = {'star': [], 'my': [], 'join': []}
        my_project_list = models.ProjectInfo.objects.filter(creator=request.tracer.user)
        for row in my_project_list:
            if row.star:
                project_dict['star'].append({'value': row, 'type': 'my'})
            else:
                project_dict['my'].append(row)
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dict['star'].append({'value': item.project, 'type': 'join'})
            else:
                project_dict['join'].append(item.project)

        form = ProjectModelForm(request)
        return render(request, 'project_list.html', {'form': form, 'project_dict': project_dict})
    form = ProjectModelForm(request, data=request.POST)
    if form.is_valid():
        # 为项目创建一个桶,名称唯一
        bucket = '{}-{}-1302167637'.format(request.tracer.user.mobile_phone, str(int(time.time())))
        region = 'ap-nanjing'
        create_bucket(bucket,region)
        # 验证通过:项目名、颜色、描述
        form.instance.creator = request.tracer.user
        form.instance.bucket = bucket
        form.instance.region = region
        # 创建项目
        form.save()
        return JsonResponse({'status': True, })
    return JsonResponse({'status': False, 'error': form.errors})


def project_star(request, project_type, project_id):
    """星标项目"""
    if project_type == 'my':
        models.ProjectInfo.objects.filter(id=project_id, creator=request.tracer.user).update(star=True)

        return redirect('project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user_id=request.tracer.user.id).update(star=True)
        return redirect('project_list')
    return HttpResponse('请求错误')


def project_unstar(request, project_type, project_id):
    if project_type == 'my':
        models.ProjectInfo.objects.filter(id=project_id, creator=request.tracer.user).update(star=False)
        return redirect('project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user_id=request.tracer.user.id).update(star=False)
        return redirect('project_list')
    return HttpResponse('请求错误')
