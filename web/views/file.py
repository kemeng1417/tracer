import json
import requests
from django.shortcuts import render, reverse
from web.forms.file import FolderModelForm, FileModelForm
from django.forms import model_to_dict
from django.http import JsonResponse
from web import models
from utils.tencent.cos import delete_file, delete_file_list, credential
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# http://127.0.0.1:8000/manage/1/file/?folder=1
def file(request, project_id):
    """ 文件列表 & 添加文件夹"""
    parent_object = None
    folder_id = request.GET.get('folder', '')
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=int(folder_id), file_type=2,
                                                             project=request.tracer.project).first()
    if request.method == 'GET':
        # 循环获取文件夹列表
        breadcrumb_list = []
        parent = parent_object
        while parent:
            # breadcrumb_list.insert(0, {'id': parent.id, 'name': parent.name})
            breadcrumb_list.insert(0, model_to_dict(parent, ['id', 'name']))
            parent = parent.parent

        # 当前目录下所有的文件和文件夹获取到
        queryset = models.FileRepository.objects.filter(project=request.tracer.project)
        if parent_object:
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')
        form = FolderModelForm(request, parent_object)
        context = {
            'form': form,
            'file_object_list': file_object_list,
            'breadcrumb_list': breadcrumb_list,
            'folder_object': parent_object,
        }
        return render(request, 'file.html', context)

    # 添加文件夹&文件夹的修改
    fid = request.POST.get('fid', '')
    edit_object = None
    if fid.isdecimal():
        edit_object = models.FileRepository.objects.filter(id=int(fid), file_type=2,
                                                           project=request.tracer.project).first()
    if edit_object:
        # 编辑
        form = FolderModelForm(request, parent_object, data=request.POST, instance=edit_object)
    else:
        # 添加
        form = FolderModelForm(request, parent_object, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


# http://127.0.0.1:8000/manage/1/file/?fid=1
def file_delete(request, project_id):
    """ 删除文件 """
    fid = request.GET.get('fid')
    # 删除数据库中的文件夹以及文件夹下面的所有文件
    delete_object = models.FileRepository.objects.filter(id=fid, project=request.tracer.project).first()
    if delete_object.file_type == 1:
        # 字节
        # 删除文件时，将容量还给当前项目的已使用空间
        request.tracer.project.use_space -= delete_object.file_size
        request.tracer.project.save()

        # cos中删除
        delete_file(request.tracer.project.bucket, request.tracer.project.region, delete_object.key)
        delete_object.delete()
        # 删除文件（数据库文件删除，cos文件删除，项目已使用空间容量还回去)
        return JsonResponse({'status': True})
    # 找到文件夹下所有的文件，对所有的文件 -->删除文件（数据库文件删除，cos文件删除，项目已使用空间容量还回去)
    total_size = 0
    key_list = []
    folder_list = [delete_object, ]
    for folder in folder_list:
        child_list = models.FileRepository.objects.filter(parent=folder, project=request.tracer.project).order_by(
            '-file_type')
        for child in child_list:
            if child.file_type == 2:
                folder_list.append(child)
            else:
                total_size += child.file_size
                key_list.append({'Key': child.key})
    # cos 批量删除文件
    if key_list:
        delete_file_list(request.tracer.project.bucket, request.tracer.project.region, key_list)

    # 归还容量
    if total_size:
        request.tracer.project.use_space -= total_size
        request.tracer.project.save()
    # 删除数据库中的文件
    delete_object.delete()
    return JsonResponse({'status': True})


@csrf_exempt
def cos_credential(request, project_id):
    """ 获取cos上传临时凭证 """
    # 数据库中存的文件大小为m，获取的为字节大小
    per_file_limit = request.tracer.price_policy.per_file_size * 1024 * 1024
    project_space = request.tracer.price_policy.project_space * 1024 * 1024 * 1024
    project_use_space = request.tracer.project.use_space
    total_size = 0
    file_list = json.loads(request.body.decode('utf-8'))
    for item in file_list:
        if item['size'] > per_file_limit:
            msg = '单文件大小超过最大限制{}，文件名：{}，请升级套餐！'.format(per_file_limit, item['name'])
            return JsonResponse({'status': False, 'error': msg})
        total_size += item['size']
    if project_use_space + total_size > project_space:
        msg = '文件空间不足，请升级套餐！'
        return JsonResponse({'status': False, 'error': msg})
    data_dict = credential(request.tracer.project.bucket, request.tracer.project.region)
    return JsonResponse({'status': True, 'data': data_dict})


@csrf_exempt
def file_post(request, project_id):
    """ 已上传成功的文件写入到数据库 """
    """  
        name: fileName,
        key: key,
        file_size: fileSize,
        parent: CURRENT_FOLDER_ID,
        etag:data.ETag,
        file_path:data.location,
    """

    # 根据key再去cos获取文件Etag
    # 把获取的数据写入到数据库
    form = FileModelForm(request, data=request.POST)
    if form.is_valid():
        # 校验通过，写入数据库
        # form.instance.file_type = 1
        # form.instance.update_user = request.tracer.user
        # form.save()
        data_dict = form.cleaned_data
        data_dict.pop('etag')
        data_dict.update({'project': request.tracer.project, 'file_type': 1, 'update_user': request.tracer.user})
        instance = models.FileRepository.objects.create(**data_dict)

        # 项目的已使用空间：更新
        request.tracer.project.use_space += data_dict['file_size']
        request.tracer.project.save()
        result = {
            'name': instance.name,
            'id': instance.id,
            'file_size': instance.file_size,
            'username': instance.update_user.username,
            'datetime': instance.update_datetime.strftime('%Y{}%m{}%d{} %H:%M').format('年', '月', '日'),
            'download_url': reverse('file_download', kwargs={'project_id': project_id, 'file_id': instance.id}),
            # 'file_type':instance.get_file_type_display(),
        }
        return JsonResponse({'status': True, 'data': result})
    return JsonResponse({'status': False, 'data': '文件错误'})


def file_download(request, project_id, file_id):
    """ 下载文件 """
    # 文件内容
    # 响应头

    file_object = models.FileRepository.objects.filter(id=file_id, project_id=project_id).first()
    res = requests.get(file_object.file_path)
    # data = res.content
    # 文件分块处理（适用于大文件）
    data = res.iter_content()

    # 设置content_type = application/octet-stream 用户提示下载框
    response = HttpResponse(data, content_type="application/octet-stream")
    from django.utils.encoding import escape_uri_path
    # 设置响应头：中文文件名转义
    response['Content-Disposition'] = 'attachment; filename={};'.format(escape_uri_path(file_object.name))
    return response
