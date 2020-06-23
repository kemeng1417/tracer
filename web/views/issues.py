from django.shortcuts import render
from web.forms.issues import IssuesModelForm
from django.http import JsonResponse
from web import models
from utils.pagination import Pagination
def issues(request, project_id):
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
        content = {'form': form, 'issues_object_list': issues_object_list, 'page_html':page_object.page_html()}

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
