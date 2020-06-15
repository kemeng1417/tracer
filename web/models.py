from django.db import models


# Create your models here.
class UserInfo(models.Model):
    """用户表"""
    username = models.CharField(max_length=32, verbose_name='用户名', db_index=True)  # 检索速度会加快
    email = models.EmailField(max_length=32, verbose_name='邮箱')
    password = models.CharField(max_length=32, verbose_name='密码')
    mobile_phone = models.CharField(max_length=32, verbose_name='手机号')


class PricePolicy(models.Model):
    """价格策略表"""
    category_choices = ((1, '免费版'), (2, '收费版'), (3, '其他'))
    # 小整数
    category = models.SmallIntegerField(verbose_name='收费类型', choices=category_choices, default=1)
    title = models.CharField(max_length=32, verbose_name='标题')
    # 正整数类型
    price = models.PositiveIntegerField(verbose_name='价格')
    project_num = models.PositiveIntegerField(verbose_name='项目数')
    project_member = models.PositiveIntegerField(verbose_name='项目成员数')
    project_space = models.PositiveIntegerField(verbose_name='项目空间')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件大小(M)')
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Transaction(models.Model):
    """用户交易表"""
    status_choices = ((2, '已支付'), (1, '待支付'))
    status = models.IntegerField(choices=status_choices, verbose_name='支付状态')
    user = models.ForeignKey(to='UserInfo', verbose_name='用户')
    price_policy = models.ForeignKey(to='PricePolicy', verbose_name='价格策略')
    count = models.IntegerField(verbose_name='数量(年)', help_text='0表示无限期')
    price = models.IntegerField(verbose_name='实际支付')
    start_time = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    order = models.CharField(max_length=64, unique=True, verbose_name='订单号')


class ProjectInfo(models.Model):
    color_choices = ((0, '#00F5FF'),
                     (1, '#00FF00'),
                     (2, '#0000FF'),
                     (3, '#CD5C5C'),
                     (4, '#FF00FF'),
                     (5, '#9A32CD'))
    name = models.CharField(max_length=32, verbose_name='项目名称')
    desc = models.CharField(max_length=256, verbose_name='项目描述', null=True, blank=True)
    color = models.SmallIntegerField(choices=color_choices, verbose_name='项目颜色', default=1)
    star = models.BooleanField(default=False, verbose_name='星标')
    use_space = models.IntegerField(verbose_name='项目已使用的空间', default=0)

    join_count = models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo')
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    # 创建cos桶
    bucket = models.CharField(verbose_name='cos桶', max_length=128)
    region = models.CharField(verbose_name='cos区域', max_length=32)

class ProjectUser(models.Model):
    """项目参与者"""
    project = models.ForeignKey(to='ProjectInfo', verbose_name='项目')
    user = models.ForeignKey(to='UserInfo', verbose_name='用户')
    star = models.BooleanField(default=False, verbose_name='星标')

    create_datetime = models.DateTimeField(verbose_name='加入时间', auto_now_add=True)


class Wiki(models.Model):
    title = models.CharField(max_length=32, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    depth = models.IntegerField(verbose_name='深度', default=1)
    parent = models.ForeignKey(blank=True, null=True, to='Wiki',
                               verbose_name='父文章')

    project = models.ForeignKey(to='ProjectInfo', verbose_name='项目')

    def __str__(self):
        return self.title