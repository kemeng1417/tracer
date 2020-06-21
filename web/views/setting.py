from django.shortcuts import render, redirect
from utils.tencent.cos import delete_bucket
from web import models
def setting(request, project_id):
    """ 系统设置 """
    return render(request, 'setting.html')


def setting_delete(request, project_id):
    """ 删除项目 """
    if request.method == 'GET':
        return render(request, 'setting_delete.html')

    project_name = request.POST.get('project_name')
    if not project_name or project_name != request.tracer.project.name:
        return render(request, 'setting_delete.html', {'error': '项目名错误'})

    # 项目名写对了删除
    if request.tracer.user != request.tracer.project.creator:
        return render(request, 'setting_delete.html', {'error': '只有项目创建者可删除项目'})

    # 删除桶
    # - 删除桶中的所有文件
    # - 删除桶中的所有碎片
    # - 删除桶
    # 删除项目
    # - 项目删除
    delete_bucket(request.tracer.project.bucket, request.tracer.project.region)

    models.ProjectInfo.objects.filter(id=request.tracer.project.id).delete()
    return redirect('project_list')
