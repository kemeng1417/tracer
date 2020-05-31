from django.db import models

# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(max_length=32, verbose_name='用户名', db_index=True)  # 检索速度会加快
    email = models.EmailField(max_length=32, verbose_name='邮箱')
    password = models.CharField(max_length=32, verbose_name='密码')
    mobile_phone = models.CharField(max_length=32, verbose_name='手机号')