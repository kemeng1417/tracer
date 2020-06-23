from django.shortcuts import render
from web.forms.issues import IssuesModelForm, IssuesReplyForm
from django.http import JsonResponse
from web import models
from utils.pagination import Pagination
from django.views.decorators.csrf import csrf_exempt

def issues(request, project_id):
    """ 问题展示及添加 """
    if request.method == 'GET':
        queryset = models.Issues.objects.filter(project=request.tracer.project)
        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
        )
        issues_object_list = queryset[page_object.start:page_object.end]
        form = IssuesModelForm(request)
        content = {'form': form, 'issues_object_list': issues_object_list, 'page_html': page_object.page_html()}

        return render(request, 'issues.html', content)

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        # 添加问题
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


# def issues_add(request, project_id):
#     return None
def issues_detail(request, project_id, issues_id):
    """ 编辑问题 """
    issues_object = models.Issues.objects.filter(project_id=project_id, id=issues_id).first()
    form = IssuesModelForm(request, instance=issues_object)
    return render(request, 'issues_detail.html', {'form': form, 'issues_object': issues_object})


@csrf_exempt
def issues_record(request, project_id, issues_id):
    """ 初始化操作记录 """
    if request.method == 'GET':
        reply_list = models.IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.tracer.project)

        # 将queryset格式化为Json数据
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }
            data_list.append(data)
        return JsonResponse({'status': True, 'data': data_list})

    form = IssuesReplyForm(request.POST)
    if form.is_valid():
        form.instance.creator = request.tracer.user
        form.instance.reply_type = 2
        form.instance.issues_id = issues_id
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }
        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': True, 'error': form.errors})
