from django.shortcuts import render,reverse,redirect
from web.forms.wiki import WikiModelForm

def wiki(request, project_id):
    """ wiki首页 """

    return render(request, 'wiki.html')


def wiki_add(request, project_id):
    """ 添加wiki文章 """
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_add.html', {'form':form})
    form = WikiModelForm(request,request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.save()
        url = reverse('wiki', kwargs={'project_id':project_id})
        return redirect(url)
    return render(request, 'wiki_add.html', {'form':form})