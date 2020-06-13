from django.shortcuts import render
from web.forms.project import ProjectModelForm
from django.http import JsonResponse
from web import models

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
        project_dict = {'star':[],'my':[],'join':[]}
        my_project_list = models.ProjectInfo.objects.filter(creator=request.tracer.user)
        for row in my_project_list:
            if row.star:
                project_dict['star'].append(row)
            else:
                project_dict['my'].append(row)
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dict['star'].append(item.project)
            else:
                project_dict['join'].append(item.project)

        form = ProjectModelForm(request)
        return render(request, 'project_list.html', {'form': form, 'project_dict':project_dict})
    form = ProjectModelForm(request, data=request.POST)
    if form.is_valid():
        # 验证通过:项目名、颜色、描述
        form.instance.creator = request.tracer.user
        # 创建项目
        form.save()
        return JsonResponse({'status': True, })
    return JsonResponse({'status': False, 'error': form.errors})
