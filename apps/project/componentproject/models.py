
from django.db import models
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.bom.component.models import ComponentVersion, ComponentCategory
from apps.bom.middleparts.models import MiddlePartsVersion

from apps.bom.subunit.models import SubUnitVersion
from apps.project.subunitproject.models import SubUnitProject
from apps.bom.productline.models import ProductLine


class ComponentProject(models.Model):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '开发预备'),
        (2, '开发阶段'),
        (3, '试产阶段'),
        (4, '量产阶段'),
        (5, '停产阶段'),
        (6, '开发中止')
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '未标记单据不可审核'),
        (2, '处理意见为空'),
        (3, '返回的单据无返回单号'),
        (4, '理赔必须设置需理赔才可以审核'),
        (5, '驳回原因为空'),
        (6, '无反馈内容, 不可以审核'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '确认开发'),
        (2, '确认更新'),
        (3, '确认组项'),
    )

    CATEGORY_LIST = (
        (1, '开发构建'),
        (2, '版本变更'),
    )
    name = models.CharField(unique=True, max_length=90, verbose_name='组项项目名', db_index=True, help_text='组项项目名')
    code = models.CharField(max_length=50, unique=True, verbose_name='组项项目编码', help_text='组项项目编码')
    category = models.SmallIntegerField(choices=CATEGORY_LIST, default=1, verbose_name='类型', help_text='类型')
    subunit_project = models.ForeignKey(SubUnitProject, null=True, blank=True, on_delete=models.CASCADE, verbose_name='子项项目', help_text='子项项目')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, verbose_name='产品系列', help_text='产品系列')

    component_version = models.OneToOneField(ComponentVersion, null=True, blank=True, on_delete=models.CASCADE, verbose_name='组项版本', help_text='组项版本')
    component_category = models.ForeignKey(ComponentCategory, on_delete=models.CASCADE, verbose_name='类型', help_text='类型')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

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
        return str(self.id)


class LogComponentProject(models.Model):

    obj = models.ForeignKey(ComponentProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-组项目-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_component_logging'

    def __str__(self):
        return str(self.id)


class CPFiles(models.Model):
    name = models.CharField(max_length=150, verbose_name='文件名称', help_text='文件名称')
    suffix = models.CharField(max_length=100, verbose_name='文件类型', help_text='文件类型')
    url = models.CharField(max_length=250, verbose_name='URL地址', help_text='URL地址')
    workorder = models.ForeignKey(ComponentProject, on_delete=models.CASCADE, verbose_name='组项项目', help_text='组项项目')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-整机项目-图片'
        verbose_name_plural = verbose_name
        db_table = 'project_component_files'

    def __str__(self):
        return str(self.id)

