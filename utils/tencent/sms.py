from qcloudsms_py import SmsSingleSender, SmsMultiSender
from qcloudsms_py.httpclient import HTTPError
from django.conf import settings

def send_sms_single(phone_num, template_id, template_param_list):
    # 短信应用 SDK AppID
    appid = settings.TENCENT_SMS_APP_ID  # SDK AppID 以1400开头
    # 短信应用 SDK AppKey
    appkey = settings.TENCENT_SMS_APP_KEY
    # 签名
    sms_sign = settings.TENCENT_SMS_APP_SIGN
    sender = SmsSingleSender(appid, appkey)
    try:
        response = sender.send_with_param(86, phone_num, template_id, template_param_list, sign=sms_sign, extend="", ext="")
    except HTTPError as e:
        response = {'result':1000, 'errmsg':'网络异常发送失败'}
    return response


def send_sms_multi(phone_num_list, template_id, param_list):
    appid = settings.TENCENT_SMS_APP_ID  # SDK AppID 以1400开头
    # 短信应用 SDK AppKey
    appkey = settings.TENCENT_SMS_APP_KEY
    # 签名
    sms_sign = settings.TENCENT_SMS_APP_SIGN
    sender = SmsMultiSender(appid, appkey)
    try:
        response = sender.send_with_param(86, phone_num_list, template_id, param_list, sign=sms_sign, extend="", ext="")
    except HTTPError as e:
        response = {'result':1000, 'errmsg':'网络异常发送失败'}
    return response

