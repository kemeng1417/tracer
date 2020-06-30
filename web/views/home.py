import datetime
import json
from utils.alipay import AliPay
from django_redis import get_redis_connection
from django.shortcuts import render, redirect
from web import models
from utils.encrypt import uid
from django.conf import settings


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
    key = 'payment_{}'.format(request.tracer.user.mobile_phone)
    conn.set(key, json.dumps(context), ex=60 * 30)
    context['policy_object'] = policy_object
    context['transaction'] = _object
    return render(request, 'payment.html', context)


"""
def pay(request):

   conn = get_redis_connection()
   key = 'payment_{}'.format(request.tracer.user.mobile_phone)
   context_string = conn.get(key)
   if not context_string:
       return redirect('price')

   context = json.loads(context_string.decode('utf-8'))

   # 1 数据库中生成交易记录, 支付成功后订单状态更新为已支付，且需要添加开始和结束的时间
   order_id = uid(request.tracer.user.mobile_phone)
   pay_price = context['pay_price']
   models.Transaction.objects.create(
       status=1,
       order=order_id,
       user=request.tracer.user,
       price_policy_id=context['price_id'],
       count=context['number'],
       price=pay_price,
   )

   # 2 跳转到支付宝进行支付
   # 根据申请的支付信息+支付宝文档生成跳转链接

   # 生成支付宝的链接
   # 跳转到该链接
   # 构造字典
   params = {
       'app_id': '2016102600763653',
       'method': 'alipay.trade.page.pay',
       'format': 'JSON',
       'return_url': 'http://127.0.0.1:8000/pay/notify/',
       'notify_url': 'http://127.0.0.1:8000/pay/notify/',
       'charset': 'utf-8',
       'sign_type': 'RSA2',
       'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
       'version': '1.0',
       'biz_content': json.dumps({
           'out_trade_no': order_id,
           'product_code': 'FAST_INSTANT_TRADE_PAY',
           'total_amount': pay_price,
           'subject': 'tracer payment',
       }, separators=(',', ':')),
   }

   # 获取待签名的字符串
   unsigned_string = '&'.join(['{0}={1}'.format(k, params[k]) for k in sorted(params)])
   # 签名 SHA256WithRSA
   from Crypto.PublicKey import RSA
   from Crypto.Signature import PKCS1_v1_5
   from Crypto.Hash import SHA256
   from base64 import decodebytes, encodebytes

   # SHA256WithRSA+应用私钥.txt 对待签名字符串进行签名
   private_key = RSA.importKey(open('files/应用私钥.txt').read())
   signer = PKCS1_v1_5.new(private_key)
   signature = signer.sign(SHA256.new(unsigned_string.encode('utf-8')))

   # 对签名之后的执行base64编码，转换为字符串
   sign_string = encodebytes(signature).decode('utf8').replace('\n', '')

   # 把生成的签名赋值给sign参数，拼接到请求参数中
   from urllib.parse import quote_plus
   result = '&'.join(['{0}={1}'.format(k, quote_plus(params[k])) for k in sorted(params)])
   result = result + '&sign=' + quote_plus(sign_string)

   gateway = 'https://openapi.alipaydev.com/gateway.do'
   ali_pay_url = '{}?{}'.format(gateway, result)
   return redirect(ali_pay_url)

"""


def pay(request):
    """ 生成订单，支付宝支付页面 """

    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.user.mobile_phone)
    context_string = conn.get(key)
    if not context_string:
        return redirect('price')

    context = json.loads(context_string.decode('utf-8'))

    # 1 数据库中生成交易记录, 支付成功后订单状态更新为已支付，且需要添加开始和结束的时间
    order_id = uid(request.tracer.user.mobile_phone)
    pay_price = context['pay_price']
    models.Transaction.objects.create(
        status=1,
        order=order_id,
        user=request.tracer.user,
        price_policy_id=context['price_id'],
        count=context['number'],
        price=pay_price,
    )
    print(settings.ALI_PRIVATE_KEY_PATH)
    ali_pay = AliPay(
        appid=settings.ALI_APPID,
        app_notify_url=settings.ALI_NOTIFY_URL,
        app_private_key_path=settings.ALI_PRIVATE_KEY_PATH,
        alipay_public_key_path=settings.ALI_PUBLIC_KEY_PATH,
        return_url=settings.ALI_RETURN_URL,
    )

    query_params = ali_pay.direct_pay(
        subject='tracer payment',
        out_trade_no=order_id,
        total_amount=pay_price,
    )

    pay_url = '{}?{}'.format(settings.ALI_GATEWAY, query_params)
    return redirect(pay_url)
