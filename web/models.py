from django.db import models


# Create your models here.
class UserInfo(models.Model):
    """用户表"""
    username = models.CharField(max_length=32, verbose_name='用户名', db_index=True)  # 检索速度会加快
    email = models.EmailField(max_length=32, verbose_name='邮箱')
    password = models.CharField(max_length=32, verbose_name='密码')
    mobile_phone = models.CharField(max_length=32, verbose_name='手机号')

    def __str__(self):
        return self.username


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
    project_space = models.PositiveIntegerField(verbose_name='项目空间', help_text='G')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件大小', help_text='M')
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
    """ 项目 """
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
    use_space = models.BigIntegerField(verbose_name='项目已使用的空间', default=0, help_text='字节')

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


class FileRepository(models.Model):
    """ 文件库 """
    type_choices = ((1, '文件'), (2, '文件夹'))
    project = models.ForeignKey('ProjectInfo', verbose_name='项目')
    name = models.CharField(verbose_name='文件名', max_length=128, help_text='文件名/文件夹名')
    file_type = models.SmallIntegerField(choices=type_choices)
    # int 类型
    file_size = models.BigIntegerField(verbose_name='文件大小', null=True, blank=True, help_text='字节')
    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True, blank=True)
    parent = models.ForeignKey(to='self', verbose_name='父目录', related_name='child', null=True, blank=True)
    update_user = models.ForeignKey('UserInfo', verbose_name='最新更新者')
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    key = models.CharField(verbose_name='文件存储在cos中的KEY', max_length=128, null=True, blank=True)


class Module(models.Model):
    """ 模块里程碑 """
    project = models.ForeignKey(verbose_name='项目', to=ProjectInfo)
    title = models.CharField(verbose_name='模块名称', max_length=32)

    def __str__(self):
        return self.title


class IssuesType(models.Model):
    """ 问题类型 """

    PROJECT_INIT_LIST = ['任务','功能','Bug']
    title = models.CharField(verbose_name='问题类型名称', max_length=32)
    project = models.ForeignKey(verbose_name='项目', to='ProjectInfo')

    def __str__(self):
        return self.title


class Issues(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='ProjectInfo')
    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssuesType')
    module_type = models.ForeignKey(verbose_name='模块', to=Module, null=True, blank=True)
    priority_choices = (
        ('danger', '高'),
        ('warning', '中'),
        ('success', '低'),
    )
    priority = models.CharField(choices=priority_choices, verbose_name='优先级', max_length=12, default='danger')
    # 新建、处理中、已解决、已忽略、待反馈、已关闭、重新打开
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name='状态', default=1)

    assign = models.ForeignKey(verbose_name='指派', to='UserInfo', related_name='task', null=True, blank=True)
    attention = models.ManyToManyField(verbose_name='关注者', to='UserInfo', related_name='observe', blank=True)
    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式')
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)
    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_problems')
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_update_datetime = models.DateTimeField(verbose_name='最后修改时间', auto_now=True)

    def __str__(self):
        return self.subject


class IssuesReply(models.Model):
    """ 问题回复 """
    reply_type_choices = (
        (1,'修改记录'),
        (2,'回复'),
    )
    reply_type = models.SmallIntegerField(verbose_name='类型', choices=reply_type_choices)
    issues = models.ForeignKey(verbose_name='问题', to='Issues')
    content = models.TextField(verbose_name='描述')
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_reply')
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    reply = models.ForeignKey(verbose_name='回复', to='self', null=True, blank=True)


class ProjectInvite(models.Model):
    """ 项目邀请码 """
    project = models.ForeignKey(verbose_name='项目', to='ProjectInfo')
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    count = models.PositiveIntegerField(verbose_name='数量', null=True, blank=True, help_text='空表示无数量限制')
    use_count = models.PositiveIntegerField(verbose_name='已使用数量',  default=0)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = models.IntegerField(verbose_name='有效期', choices=period_choices, default=1440)
    create_datetime = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_invite')
