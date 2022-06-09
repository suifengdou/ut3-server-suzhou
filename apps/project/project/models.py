from django.db import models
from apps.base.company.models import Company
import django.utils.timezone as timezone
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.utils.geography.models import Nationality
from apps.bom.productline.models import ProductLine
from apps.bom.units.models import UnitsVersion
from apps.bom.subunit.models import SubUnitVersion


class OriginUnitProject(models.Model):

    LEVEL_LIST = (
        (0, '无'),
        (1, 'S'),
        (2, 'A'),
        (3, 'B'),
        (4, 'C'),
    )
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

    name = models.CharField(unique=True, max_length=30, verbose_name='整机项目名', db_index=True, help_text='整机项目名')
    unit_id = models.CharField(unique=True, max_length=30, verbose_name='整机编码', db_index=True, help_text='整机编码')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, verbose_name='产品线', help_text='产品线')
    level = models.IntegerField(choices=LEVEL_LIST, default=0, verbose_name='级别', help_text='级别')
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, verbose_name='国别', help_text='国别')
    serial_number = models.IntegerField(verbose_name='系列排序', help_text='系列排序')
    unit_number = models.IntegerField(unique=True, null=True, blank=True, verbose_name='整机排序', help_text='整机排序')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-原始整机项目'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_units'

    def __str__(self):
        return self.name


class UnitProject(models.Model):

    LEVEL_LIST = (
        (0, '无'),
        (1, 'S'),
        (2, 'A'),
        (3, 'B'),
        (4, 'C'),
    )
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
    ori_project = models.OneToOneField(OriginUnitProject, on_delete=models.CASCADE, verbose_name='原始项目单', help_text='原始项目单')
    name = models.ForeignKey(UnitsVersion, on_delete=models.CASCADE, verbose_name='整机项目版本', help_text='整机项目版本')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-整机项目'
        verbose_name_plural = verbose_name
        db_table = 'project_units'

    def __str__(self):
        return str(self.name.name)


class UnitProjectDetails(models.Model):

    unit_project = models.ForeignKey(UnitProject, on_delete=models.CASCADE, verbose_name='项目', help_text='项目')
    subunit = models.ForeignKey(SubUnitVersion, on_delete=models.CASCADE, verbose_name='子项目', help_text='子项目')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-整机项目'
        verbose_name_plural = verbose_name
        db_table = 'project_units'

    def __str__(self):
        return str(self.unit_project.name)


class LogUnitProject(models.Model):

    objects = models.ForeignKey(UnitProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-原始整机项目-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_units_logging'

    def __str__(self):
        return self.name


class LogOriginUnitProject(models.Model):
    object = models.ForeignKey(OriginUnitProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-原始整机项目-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_units_logging'

    def __str__(self):
        return self.name


