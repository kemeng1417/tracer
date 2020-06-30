import datetime
import json

from django_redis import get_redis_connection
from django.shortcuts import render, redirect
from web import models
from utils.encrypt import uid


def index(request):
    return render(request, 'index.html')


def price(request):
    """ 套餐 """
    policy_list = models.PricePolicy.objects.filter(category=2)
    return render(request, 'price.html', {'policy_list': policy_list})


def payment(request, price_id):
    """ 价格策略 """
    policy_object = models.PricePolicy.objects.filter(category=2, id=price_id).first()
    if not policy_object:
        return redirect('price')
    number = request.GET.get('number', '')
    if not number or not number.isdecimal():
        return redirect('price')
    number = int(number)
    if number <= 0:
        return redirect('price')

    # 计算原价
    total_price = policy_object.price * number
    balance = 0
    _object = None
    if request.tracer.price_policy.category == 2:
        _object = models.Transaction.objects.filter(user=request.tracer.user, status=2).order_by('-id').first()
        total_timedelta = _object.end_time - _object.start_time  # 一个时间对象
        balance_timedelta = _object.end_time - datetime.datetime.now()

        if total_timedelta.days == balance_timedelta.days:
            balance = _object.price / total_timedelta.days * (balance_timedelta.days - 1)
        else:
            balance = _object.price / total_timedelta.days * balance_timedelta.days

    if balance >= total_price:
        return redirect('price')

    context = {
        'price_id': policy_object.id,
        'number': number,
        'total_price': total_price,
        'balance': round(balance, 2),
        'pay_price': total_price - round(balance, 2)
    }
    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.user.mibile_phone)
    conn.set(key, json.dumps(context), ex=60 * 30)
    context['policy_object'] = policy_object
    context['transaction'] = _object
    return render(request, 'payment.html', context)


def pay(request):
    """ 生成订单，支付宝支付页面 """
    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.user.mibile_phone)
    context_string = conn.get(key)
    if not context_string:
        return redirect('price')

    context = json.loads(context_string.decode('utf-8'))

    # 1 数据库中生成交易记录, 支付成功后订单状态更新为已支付，且需要添加开始和结束的时间
    order_id = uid(request.tracer.user.mibile_phone)
    models.Transaction.objects.create(
        status=1,
        order=order_id,
        user=request.tracer.user,
        price_policy_id=context['price_id'],
        count=context['number'],
        price=context['pay_price'],
    )

    # 2 跳转到支付宝进行支付
    # 根据申请的支付信息+支付宝文档生成跳转链接

    # 生成支付宝的链接
    # 跳转到该链接
