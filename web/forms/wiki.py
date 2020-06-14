from web import models
from django import forms
from web.forms.bootstrap import BootStrapForm

class WikiModelForm(BootStrapForm, forms.ModelForm ):
    class Meta:
        model = models.Wiki
        exclude = ['project','depth']


    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        # 找到想要的字段绑定显示的数量
        # 数据到当前项目中获取项目的标题
        total_data_list = [('','请选择'),]
        data_list = models.Wiki.objects.filter(project=self.request.tracer.project).values_list('id','title')
        # 一次后末尾添加多个值
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list


