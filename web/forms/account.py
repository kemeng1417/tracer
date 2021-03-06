import random
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from web import models
from django.conf import settings
from utils.tencent.sms import send_sms_single
from django_redis import get_redis_connection
from utils.encrypt import md5
from web.forms.bootstrap import BootStrapForm


class RegisterModelForm(BootStrapForm, forms.ModelForm):
    # 可以重写字段，在模板中显示,使用validators写正则
    mobile_phone = forms.CharField(label='手机号', validators=[
        RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机格式错误'), ])
    # 修改密码的插件
    password = forms.CharField(label='密码', widget=forms.PasswordInput(),
                               min_length=8,
                               max_length=64,
                               error_messages={
                                   'min_length': '密码长度不能小于8个字符',
                                   'max_length': '密码长度不能大于64个字符',
                               })
    # 添加标签属性
    re_password = forms.CharField(label='重复密码', widget=forms.PasswordInput(),
                                  min_length=8,
                                  max_length=64,
                                  error_messages={
                                      'min_length': '密码长度不能小于8个字符',
                                      'max_length': '密码长度不能大于64个字符',
                                  }
                                  )
    code = forms.CharField(label='验证码', widget=forms.TextInput())

    class Meta:
        model = models.UserInfo
        # fields = "__all__"
        fields = ['username', 'email', 'password', 're_password',
                  'mobile_phone', 'code']

    def clean_username(self):
        username = self.cleaned_data['username']
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('邮箱已存在')
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        # 加密并返回

        return md5(password)

    # 按字段顺序校验
    def clean_re_password(self):
        # 此处获取到的是MD5加密以后的password，使用get获取避免出错
        password = self.cleaned_data.get('password')
        re_password = md5(self.cleaned_data['re_password'])
        if password != re_password:
            raise ValidationError('两次密码不一致')
        return re_password

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已注册')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        # mobile_phone = self.cleaned_data['mobile_phone']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        # 先判断是否填写了手机号，如果没有返回code
        if not mobile_phone:
            return code
        # 调用django-redis获取redis里按手机号存储的键值对，get
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送,请重新发送')
        # 从redis中获取的都是编码后的字符串，需要解码
        redis_str_code = redis_code.decode('utf-8')
        # 去除空格后进行比较
        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误,请重新输入')
        return code


class SendSmsForm(forms.Form):
    """手机号校验的钩子"""
    mobile_phone = forms.CharField(label='手机号',
                                   validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机格式错误'), ])

    # 如果想用视图函数里的参数,需要重写init方法
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """验证钩子"""
        mobile_phone = self.cleaned_data.get('mobile_phone')

        # 为了判断使用的是哪个模板，需要前端将tpl传过来
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_APP_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError('短信模板错误')
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        # 判断是注册还是登陆操作
        if tpl == 'login':
            if not exists:
                raise ValidationError('手机号不存在,请先注册')
        else:
            if exists:
                raise ValidationError('手机号已存在')

        # 发短信
        code = random.randrange(1000, 9999)
        print(code)
        sms = send_sms_single(mobile_phone, template_id, [code, ])
        if sms['result'] != 0:
            raise ValidationError('短信发送失败,{}'.format(sms['errmsg']))
        # 验证码写入redis，设置超时时间为60s
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)

        return mobile_phone


class LoginSMSForm(BootStrapForm, forms.Form):
    """登陆验证码钩子"""
    mobile_phone = forms.CharField(label='手机号', validators=[
        RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机格式错误'), ])
    code = forms.CharField(label='验证码', widget=forms.TextInput())

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        # exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        # 省去重复查询的操作，user_object 返回给views
        user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        if not user_object:
            raise ValidationError('手机号不存在')
        return user_object

    def clean_code(self):
        user_object = self.cleaned_data.get('mobile_phone')
        code = self.cleaned_data['code']

        # 手机号不存在,不校验验证码
        if not user_object:
            return code

        conn = get_redis_connection()
        redis_code = conn.get(user_object.mobile_phone, )
        if not redis_code:
            raise ValidationError('验证码失效或未发送,请重新发送')
        redis_str_code = redis_code.decode('utf-8')
        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误,请重新输入')
        return code


class LoginForm(BootStrapForm, forms.Form):
    username = forms.CharField(label='邮箱或手机号')
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='图片验证码')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_password(self):
        password = self.cleaned_data['password']
        return md5(password)

    def clean_code(self):
        """钩子 图片验证码是否正确"""
        # 读取用户输入的验证码
        code = self.cleaned_data['code']
        # 在session中获取自己的验证码
        session_code = self.request.session.get('image_code')
        if not session_code:
            raise ValidationError('验证码已过期，请重新获取')

        if not code.strip().upper() == session_code:
            raise ValidationError('验证码输入错误')

        return code
