"""
用户账户相关功能:注册 短信 登录 注销
"""
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSMSForm, LoginForm
from web import models
from django.db.models import Q


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
        return render(request, 'login_sms.html', {'form': form})

    form = LoginSMSForm(request.POST)
    if form.is_valid():
        user_object = form.cleaned_data['mobile_phone']
        # 保存用户名到session中
        request.session['user_id'] = user_object.pk
        request.session.set_expiry(60 * 60 * 24 * 14)
        return JsonResponse({'status': True, 'data': '/index/'})
    return JsonResponse({'status': False, 'error': form.errors})


def login(request):
    if request.method == 'GET':
        form = LoginForm(request)
        return render(request, 'login.html', {'form': form})
    form = LoginForm(request, request.POST)

    if form.is_valid():
        print('eee')
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        # user_object = models.UserInfo.objects.filter(username=username,password=password).first()
        user_object = models.UserInfo.objects.filter(Q(email=username) | Q(mobile_phone=username)).filter(
            password=password).first()
        if user_object:
            request.session['user_id'] = user_object.pk
            request.session.set_expiry(60 * 60 * 24 * 14)
            return redirect('index')
        form.add_error('username', '用户名或密码错误')
    return render(request, 'login.html', {'form': form})


def img_code(request):
    """读取验证码到内存后返回给页面"""
    from utils.image_code import check_code
    from io import BytesIO
    img, code = check_code()
    request.session['image_code'] = code
    # 设置超时时间，直接在session中操作，不用redis
    request.session.set_expiry(60)
    # 读取到内存中
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def logout(request):
    request.session.flush()
    return redirect('index')