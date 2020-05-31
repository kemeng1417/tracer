"""
用户账户相关功能:注册 短信 登录 注销
"""
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from web.forms.account import RegisterModelForm, SendSmsForm
from web import models


def register(request):
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'register.html', {'form': form})
    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        # 验证通过,密码保存为密文
        form.save()
        # instance = models.UserInfo.objects.create(**form.cleaned_data),如果这么写需要移除没有用的字段
        return JsonResponse({'status': True, 'data': '/login/'})

    return JsonResponse({'status': False, 'error': form.errors})


def send_sms(request):
    # 开始调用函数校验
    form = SendSmsForm(request, data=request.GET)

    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})
