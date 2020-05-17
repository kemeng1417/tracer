from django.shortcuts import render, HttpResponse
from utils.tencent.sms import send_sms_single
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from app01 import models
# Create your views here.
import random

def send(request):
    """发送短信"""
    tpl = request.GET.get('tpl')
    template_id = settings.TENCENT_SMS_APP_TEMPLATE.get(tpl)
    code = random.randrange(1000,9999)
    res = send_sms_single('1309893511', template_id, [code,])
    if res['result'] == 0 :
        return HttpResponse('成功')
    else:
        return HttpResponse(res['errmsg'])


class RegisterModelForm(forms.ModelForm):
    # 可以重写字段，在模板中显示,使用validators写正则
    mobile_phone = forms.CharField(label='手机号', validators=[
        RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机格式错误'), ])
    # 修改密码的插件
    password = forms.CharField(label='密码',widget=forms.PasswordInput())
    # 添加标签属性
    re_password = forms.CharField(label='重复密码',widget=forms.PasswordInput())
    code = forms.CharField(label='验证码', widget=forms.TextInput())
    class Meta:
        model = models.UserInfo
        # fields = "__all__"
        fields = ['username', 'email', 'password', 're_password',
                  'mobile_phone', 'code']
    # 重写父类方法，加上class
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'请输入{field.label}'

def register(request):
    form = RegisterModelForm()
    return render(request, 'register.html', {'form': form})