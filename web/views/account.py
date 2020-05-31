"""
用户账户相关功能:注册 短信 登录 注销
"""
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSMSForm
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


def login_sms(request):
    """ 短信登录 """
    if request.method == 'GET':
        form = LoginSMSForm()
        return render(request, 'login_sms.html', {'form':form})

    form = LoginSMSForm(request.POST)
    if form.is_valid():
        user_object = form.cleaned_data['mobile_phone']
        # 保存用户名到session中
        request.session['user_id'] = user_object.pk
        request.session['user_name'] = user_object.username
        return JsonResponse({'status':True,'data':'/index/'})
    return JsonResponse({'status':False,'error':form.errors})
