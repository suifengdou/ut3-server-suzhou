
from django.db import models
from apps.bom.productline.models import ProductLine
from apps.utils.geography.models import Nationality
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.bom.mould.models import Mould, MouldVersion, MouldVersionDetails
from apps.bom.middleparts.models import MiddlePartsVersion


class MouldProject(models.Model):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '等待递交'),
        (2, '等待处理'),
        (3, '等待执行'),
        (4, '终审复核'),
        (5, '财务审核'),
        (6, '工单完结')
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '快递单号错误'),
        (2, '处理意见为空'),
        (3, '返回的单据无返回单号'),
        (4, '理赔必须设置需理赔才可以审核'),
        (5, '驳回原因为空'),
        (6, '无反馈内容, 不可以审核'),
    )
    PROCESSTAG = (
        (0, '未分类'),
        (1, '待截单'),
        (2, '签复核'),
        (3, '改地址'),
        (4, '催派查'),
        (5, '丢件核'),
        (6, '纠纷中'),
        (7, '需理赔'),
        (8, '其他类'),
    )
    CATEGORY_LIST = (
        (1, '新建'),
        (2, '更新'),
    )

    name = models.CharField(max_length=50, unique=True, verbose_name='模具项目名称', help_text='模具项目名称')
    mould_id = models.CharField(max_length=50, unique=True, verbose_name='模具项目编码', help_text='模具项目编码')
    mould_version = models.ForeignKey(MouldVersion, null=True, blank=True, on_delete=models.CASCADE, verbose_name='模具项目版本', help_text='模具项目版本')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    category = models.SmallIntegerField(choices=CATEGORY_LIST, default=1, verbose_name='工单类型', help_text='工单类型')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-组项目'
        verbose_name_plural = verbose_name
        db_table = 'project_component'

    def __str__(self):
        return self.name


class MouldProjectDetails(models.Model):

    project = models.ForeignKey(MouldProject, on_delete=models.CASCADE, verbose_name='模具项目', help_text='模具项目')
    details = models.ForeignKey(MiddlePartsVersion, on_delete=models.CASCADE, verbose_name='中间件', help_text='中间件')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-组项目'
        verbose_name_plural = verbose_name
        db_table = 'project_component_details'

    def __str__(self):
        return str(self.project.name)


class LogMouldProject(models.Model):

    objects = models.ForeignKey(MouldProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-组项目-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_component_logging'

    def __str__(self):
        return self.name

