import datetime

from django.utils.deprecation import MiddlewareMixin
from web import models
from django.conf import settings
import re
from django.shortcuts import redirect, reverse


class Tracer(object):
    """将user,price_policy封装到tracer对象中"""

    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # url = request.path_info
        # user_id = request.session.get('user_id',0)
        # if user_id:
        #     user_object = models.UserInfo.objects.filter(id=user_id).first()
        #     request.tracer = user_object
        #     return
        # # 白名单
        # for i in settings.WHITE_LIST:
        #     if re.match(i,url):
        #         return
        # return redirect('{}?url={}'.format(reverse('login'),url))
        # # return redirect('login')
        request.tracer = Tracer()
        user_id = request.session.get('user_id', 0)
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        request.tracer.user = user_object
        if request.path_info in settings.WHITE_LIST:
            return
        if not request.tracer.user:
            return redirect('login')

        # 登录成功后，访问后台管理时，获取当前账户拥有的额度
        # 方式一：免费额度在交易记录中存储
        _object = models.Transaction.objects.filter(user=user_object, status=2).order_by('-id').first()

        # 判断是否已过期
        current_datetime = datetime.datetime.now()
        if _object.end_time and _object.end_time < current_datetime:
            _object = models.Transaction.objects.filter(user=user_object, status=2, prices_policy__category=1).first()
        request.tracer.price_policy = _object.price_policy

        # 方式二：免费的额度存储配置文件

    def process_view(self, request, view, args, kwargs):

        # 判断url是否是manage开头，如果是则判断项目id是否是我创建或是我参与的
        if not request.path_info.startswith('/manage/'):
            return
        project_id = kwargs.get('project_id')

        # 判断是否是我创建
        project_object = models.ProjectInfo.objects.filter(creator=request.tracer.user, id=project_id).first()
        if project_object:
            # 如果是我创建的可以通过
            request.tracer.project = project_object
            return
        project_user_object = models.ProjectUser.objects.filter(user=request.tracer.user, project_id=project_id).first()
        if project_user_object:
            request.tracer.project = project_user_object.project
            return

        return redirect('project_list')
