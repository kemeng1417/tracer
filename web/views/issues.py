import json
import datetime
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

from web.forms.issues import IssuesModelForm, IssuesReplyForm, InviteModelForm
from django.http import JsonResponse, QueryDict
from web import models
from utils.pagination import Pagination
from django.views.decorators.csrf import csrf_exempt
from utils.encrypt import uid


class CheckFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ''
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                ck = 'checked'
                value_list.remove(key)
            else:
                value_list.append(key)

            # 生成过滤的url
            # 在当前url的基础上添加
            from django.http import QueryDict
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)  # {'status':[1,2,3],'xx':[1,]}

            # 筛选时处理分页
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:

                url = '{}?{}'.format(self.request.path_info, param_url)  # status=1&status=2&status=3&&xx=1
            else:
                url = self.request.path_info
            tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck} ><label>{text}</label></a>'
            html = tpl.format(url=url, ck=ck, text=text)
            yield mark_safe(html)


class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe('<select class="select2" multiple style="width:100%;">')
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            selected = ''
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)
            from django.http import QueryDict
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)  # {'status':[1,2,3],'xx':[1,]}

            # 筛选时处理分页
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:

                url = '{}?{}'.format(self.request.path_info, param_url)  # status=1&status=2&status=3&&xx=1
            else:
                url = self.request.path_info

            html = '<option value="{url}" {selected}>{text}</option>'.format(url=url, selected=selected, text=text)
            yield mark_safe(html)
        yield mark_safe('</select>')


def issues(request, project_id):
    """ 问题展示及添加 """
    if request.method == 'GET':
        # 筛选条件（根据用户通过GET传过来的参数
        allow_filter_list = ['issues_type', 'status', 'priority', 'assign', 'attention']
        condition = {}
        for name in allow_filter_list:
            value_list = request.GET.getlist(name)
            if not value_list:
                continue

            condition['{}__in'.format(name)] = value_list
        queryset = models.Issues.objects.filter(project=request.tracer.project).filter(**condition)
        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
        )
        issues_object_list = queryset[page_object.start:page_object.end]
        form = IssuesModelForm(request)

        issues_type_list = models.IssuesType.objects.filter(project_id=project_id).values_list('id', 'title')

        project_total_user = [(request.tracer.project.creator_id, request.tracer.project.creator.username), ]
        project_join_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id',
                                                                                                 'user__username')

        project_total_user.extend(project_join_user)

        invite_form = InviteModelForm()
        content = {
            'form': form,
            'invite_form': invite_form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'filter_list': [
                {'title': '问题类型', 'filter': CheckFilter('issues_type', issues_type_list, request)},
                {'title': '状态', 'filter': CheckFilter('status', models.Issues.status_choices, request)},
                {'title': '优先级', 'filter': CheckFilter('priority', models.Issues.priority_choices, request)},
                {'title': '指派者', 'filter': SelectFilter('assign', project_total_user, request)},
                {'title': '关注者', 'filter': SelectFilter('attention', project_total_user, request)},

            ],

        }
        return render(request, 'issues.html', content)

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        # 添加问题
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


# def issues_add(request, project_id):
#     return None
def issues_detail(request, project_id, issues_id):
    """ 编辑问题 """
    issues_object = models.Issues.objects.filter(project_id=project_id, id=issues_id).first()
    form = IssuesModelForm(request, instance=issues_object)
    return render(request, 'issues_detail.html', {'form': form, 'issues_object': issues_object})


@csrf_exempt
def issues_record(request, project_id, issues_id):
    """ 初始化操作记录 """
    if request.method == 'GET':
        reply_list = models.IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.tracer.project)

        # 将queryset格式化为Json数据
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }
            data_list.append(data)
        return JsonResponse({'status': True, 'data': data_list})

    form = IssuesReplyForm(request.POST)
    if form.is_valid():
        form.instance.creator = request.tracer.user
        form.instance.reply_type = 2
        form.instance.issues_id = issues_id
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }
        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': True, 'error': form.errors})


@csrf_exempt
def issues_change(request, project_id, issues_id):
    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
    post_dict = json.loads(request.body.decode('utf-8'))
    name = post_dict.get('name')
    value = post_dict.get('value')

    # if not name:
    #     pass
    # # 数据库字段更新
    # # 文本
    # else:
    field_object = models.Issues._meta.get_field(name)

    def create_reply_record(content):
        new_object = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=content,
            creator=request.tracer.user,
        )

        data = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.username,
            'datetime': new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': new_object.reply_id
        }

        return data

    if name in ['subject', 'desc', 'start_date', 'end_date']:
        if not value:
            if not field_object.null:
                return JsonResponse({'status': False, 'error': '您选择的值不能为空'})
            setattr(issues_object, name, None)
            issues_object.save()
            change_record = '{}更新为空'.format(field_object.verbose_name)
        else:
            setattr(issues_object, name, value)
            issues_object.save()
            change_record = '{}更新为{}'.format(field_object.verbose_name, value)

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    # fk(指派要判断是都是创建者或参与者）
    if name in ['issues_type', 'module_type', 'parent', 'assign']:
        # 选择为空
        if not value:
            # 不允许为空
            if not field_object.null:
                return JsonResponse({'status': False, 'error': '您选择的值不能为空'})
            # 允许为空
            setattr(issues_object, name, None)
            change_record = '{}更新为空'.format(field_object.verbose_name)
        else:  # 用户输入不能为空
            if name == 'assign':
                if value == str(request.tracer.project.creator_id):
                    instance = request.tracer.project.creator
                else:
                    project_user_object = models.ProjectUser.objects.filter(project_id=project_id,
                                                                            user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status': False, 'error': '您选择的值不存在'})
                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = '{}更新为{}'.format(field_object.verbose_name, str(instance))
                # 判断用户输入的值是自己的值
            else:
                instance = field_object.rel.model.objects.filter(id=value, project_id=project_id).first()
                if not instance:
                    return JsonResponse({'status': False, 'error': '您选择的值不存在'})
                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = '{}更新为{}'.format(field_object.verbose_name, str(instance))  # value根据文本获取到的内容

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})
    # choices
    if name in ['priority', 'status', 'mode', ]:
        selected_text = None
        for key, text in field_object.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'status': False, 'error': '您选择的值不存在'})
        setattr(issues_object, name, value)
        issues_object.save()
        change_record = '{}更新为{}'.format(field_object.verbose_name, selected_text)
        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})
    # M2M
    if name == 'attention':
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': '数据格式错误'})
        if not value:
            issues_object.attention.set(value)
            issues_object.save()
            change_record = '{}更新为空'.format(field_object.verbose_name)

        else:
            # value = [1,2,3,4] -->是否是项目的创建者或是参与者
            # 获取项目的所有成员
            user_dict = {str(request.tracer.project.creator_id): request.tracer.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username
            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': '用户不存在，请重新设置'})
                username_list.append(username)
            issues_object.attention.set(value)
            issues_object.save()
            change_record = '{}更新为{}'.format(field_object.verbose_name, ','.join(username_list))
        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})
    # 生成操作记录

    return JsonResponse({'status': True, 'error': 'gun'})


def invite_url(request, project_id):
    """ 生成邀请码 """
    form = InviteModelForm(data=request.POST)
    if form.is_valid():
        """
        1. 创建一个随机的邀请码
        2. 验证码保存到数据库
        3. 只有创建者才能邀请，其他成员无法创建
        """
        if request.tracer.user != request.tracer.project.creator:
            form.add_error('period', '没有权限创建邀请码')
            return JsonResponse({'status': False, 'error': form.errors})
        random_invite_code = uid(request.tracer.user.mobile_phone)
        form.instance.project = request.tracer.project
        form.instance.code = random_invite_code
        form.instance.creator = request.tracer.user
        form.save()

        # 邀请码返回前端，前端展示验证码
        url = '{scheme}://{host}{path}'.format(
            scheme=request.scheme,  # 访问的方法
            host=request.get_host(),  # 返回域名和端口
            path=reverse('invite_join', kwargs={'code': random_invite_code})
        )
        return JsonResponse({'status': True, 'data': url})
    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    """ 访问邀请码 """
    invite_object = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_object:
        return render(request, 'invite_join.html', {'error': '邀请码不存在'})
    if invite_object.project.creator == request.tracer.user:
        return render(request, 'invite_join.html', {'error': '您是创建者，无需重复加入'})
    exists = models.ProjectUser.objects.filter(project=invite_object.project, user=request.tracer.user).exists()
    if exists:
        return render(request, 'invite_join.html', {'error': '您已是参与者， 无需重复加入'})

    # 最多允许的成员
    max_member = request.tracer.price_policy.project_member

    # 目前所有成员
    current_member = models.ProjectUser.objects.filter(project=invite_object.project).count()
    current_member += 1
    if current_member >= max_member:
        return render(request, 'invite_join.html', {'error': '项目成员超限，请升级套餐'})

    current_datetime = datetime.datetime.now()
    limit_datetime = invite_object.create_datetime + datetime.timedelta(minutes=invite_object.period)
    if current_datetime > limit_datetime:
        return render(request, 'invite_join.html', {'error': '邀请码已过期'})

    # 数量限制
    if invite_object.count:
        if invite_object.use_count >= invite_object.count:
            return render(request, 'invite_join.html', {'error': '邀请码数量已使用完'})
        invite_object.use_count += 1
        invite_object.save()
    # 无数量限制
    models.ProjectUser.objects.create(user=request.tracer.user, project=invite_object.project)
    return render(request, 'invite_join.html', {'project': invite_object.project})
