from django.shortcuts import render, HttpResponse
from utils.tencent.sms import send_sms_single
from django.conf import settings
# Create your views here.
import random

def send(request):
    """发送短信"""
    tpl = request.GET.get('tpl')
    template_id = settings.TENCENT_SMS_APP_TEMPLATE.get(tpl)
    code = random.randrange(1000,9999)
    res = send_sms_single('1309893511', template_id, [code,1])
    if res['result'] == 0 :
        return HttpResponse('成功')
    else:
        return HttpResponse(res['errmsg'])