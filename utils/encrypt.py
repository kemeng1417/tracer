import hashlib
from django.conf import settings


def md5(string):
    """md5加密"""
    md5_obj = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    md5_obj.update(string.encode('utf-8'))
    return md5_obj.hexdigest()
