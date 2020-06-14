from django.shortcuts import render,reverse,redirect
from web.forms.wiki import WikiModelForm
from web import models
from django.http import JsonResponse,HttpResponse
def wiki(request, project_id):
    """ wiki首页 """
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')

    wiki_object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()

    return render(request, 'wiki.html', {'wiki_object':wiki_object})


def wiki_add(request, project_id):
    """ 添加wiki文章 """
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_add.html', {'form':form})
    form = WikiModelForm(request,request.POST)
    if form.is_valid():
        # 判断用户是否已经选择父文章
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth+1
        else:
            form.instance.depth = 1
        form.instance.project = request.tracer.project
        form.save()
        url = reverse('wiki', kwargs={'project_id':project_id})
        return redirect(url)
    return render(request, 'wiki_add.html', {'form':form})


def wiki_catalog(request, project_id):
    """ 获取wiki目录 """

    # 获取当前项目所有的目录
    # 获取到的是queryset类型，必须变成列表才能传给json
    # data = models.Wiki.objects.filter(project_id=project_id).values('id','title','parent_id')
    data = models.Wiki.objects.filter(project_id=project_id).values('id','title','parent_id').order_by('depth', 'id')
    return JsonResponse({'status':True, 'data':list(data)})


def wiki_delete(request, project_id):
    wiki_id = request.GET.get('wiki_id')
    models.Wiki.objects.filter(id=wiki_id, project_id=project_id).delete()
    url = reverse('wiki', kwargs={'project_id':project_id})
    return redirect(url)