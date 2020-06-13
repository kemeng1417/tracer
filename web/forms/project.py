from django import forms
from django.core.exceptions import ValidationError

from web.forms.bootstrap import BootStrapForm
from web import models


class ProjectModelForm(BootStrapForm, forms.ModelForm):
    # desc = forms.CharField(widget=forms.Textarea())
    class Meta:
        model = models.ProjectInfo
        fields = ['name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea,
            'color': forms.RadioSelect(attrs={'class':'radioColor'}),
            # 可以添加属性 attr={xx=xxx}
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        """项目校验钩子"""
        # 1.当前用户是否已经创建项目
        name = self.cleaned_data['name']
        exists = models.ProjectInfo.objects.filter(name=name, creator=self.request.tracer.user).exists()
        if exists:
            raise ValidationError('项目名已存在')

        # 2.当前用户是否还有额度创建项目,最多创建多少个项目

        # 现在已创建多少个项目
        count = models.ProjectInfo.objects.filter(creator=self.request.tracer.user).count()
        if count >= self.request.tracer.price_policy.project_num:
            raise ValidationError('项目个数超限，请购买套餐')
        return name
