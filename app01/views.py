from django.shortcuts import render, HttpResponse
from utils.tencent.sms import send_sms_single
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from app01 import models
# Create your views here.
import random
from django.http import JsonResponse
from django_redis import get_redis_connection

def send(request):
    """发送短信"""
    tpl = request.GET.get('tpl')
    template_id = settings.TENCENT_SMS_APP_TEMPLATE.get(tpl)
    code = random.randrange(1000, 9999)
    res = send_sms_single('1309893511', template_id, [code, ])
    if res['result'] == 0:
        return HttpResponse('成功')
    else:
        return HttpResponse(res['errmsg'])


class RegisterModelForm(forms.ModelForm):
    # 可以重写字段，在模板中显示,使用validators写正则
    mobile_phone = forms.CharField(label='手机号', validators=[
        RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机格式错误'), ])
    # 修改密码的插件
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    # 添加标签属性
    re_password = forms.CharField(label='重复密码', widget=forms.PasswordInput())
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


class SendSmsForm(forms.Form):
    """手机号校验的钩子"""
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机格式错误'), ])

    # 如果想用视图函数里的参数,需要重写init方法
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """验证钩子"""
        mobile_phone = self.cleaned_data['mobile_phone']
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_APP_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError('短信模板错误')
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已存在')

        # 发短信
        code = random.randrange(1000, 9999)
        sms = send_sms_single(mobile_phone, template_id, [code, ])
        if sms['result'] != 0:
            raise ValidationError('短信发送失败,{}'.format(sms['errmsg']))
        # 验证码写入redis
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)

        return mobile_phone


def register(request):
    form = RegisterModelForm()
    form_mobile = RegisterModelForm(request, data=request.GET)
    if request.method == 'POST':
        form = RegisterModelForm(data=request.GET)
        form_mobile = SendSmsForm(request,data=request.POST)
        if form.is_valid() and form_mobile.is_valid():
            models.UserInfo.objects.create(**form.cleaned_data)
            return JsonResponse({'status': True, })
        return JsonResponse({'status': True, 'error': form.errors})
    return render(request, 'app01/register.html', {'form': form})
