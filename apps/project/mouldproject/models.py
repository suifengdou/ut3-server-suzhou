
from django.db import models

from apps.utils.geography.models import Nationality
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.bom.mould.models import Mould, MouldVersion, MouldVersionDetails
from apps.bom.middleparts.models import MiddlePartsVersion
from apps.bom.productline.models import ProductLine
from apps.bom.units.models import Units


class OriMouldProject(models.Model):
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
        (1, '开发构建'),
        (2, '版本变更'),
    )

    name = models.CharField(max_length=60, unique=True, verbose_name='模具名', help_text='模具名')
    mould_id = models.CharField(max_length=60, unique=True, null=True, blank=True, verbose_name='模具ID', help_text='模具ID')
    category = models.SmallIntegerField(choices=CATEGORY_LIST, default=1, verbose_name='类型', help_text='类型')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, verbose_name='产品系列', help_text='产品系列')
    Units = models.ForeignKey(Units, on_delete=models.CASCADE, verbose_name='整机', help_text='整机')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-原始模具工作台'
        verbose_name_plural = verbose_name
        db_table = 'project_mould_ori'

    def __str__(self):
        return self.name


class OriMouldProjectDetails(models.Model):
    LEVEL = (
        (1, 'S'),
        (2, 'A'),
        (3, 'B'),
        (4, 'C'),
    )
    project = models.ForeignKey(OriMouldProject, on_delete=models.CASCADE, verbose_name='模具', help_text='模具')
    details = models.ForeignKey(MiddlePartsVersion, on_delete=models.CASCADE, verbose_name='中间件', help_text='中间件')
    cavity_num = models.CharField(max_length=60, null=True, blank=True, verbose_name='模穴数', help_text='模穴数')
    gate_type = models.CharField(max_length=60, null=True, blank=True, verbose_name='浇口类型', help_text='浇口类型')
    cavity_steel = models.CharField(max_length=60, null=True, blank=True, verbose_name='前模钢料', help_text='前模钢料')
    core_steel = models.CharField(max_length=60, null=True, blank=True, verbose_name='后模钢料', help_text='后模钢料')
    difficulty_level = models.SmallIntegerField(choices=LEVEL, null=True, blank=True, db_index=True, verbose_name='制造困难等级', help_text='制造困难等级')
    life_span = models.IntegerField(null=True, blank=True, verbose_name='寿命', help_text='寿命')
    file_name = models.CharField(max_length=60, verbose_name='文件名', help_text='文件名')
    surface = models.CharField(max_length=60, null=True, blank=True, verbose_name='表面处理', help_text='表面处理')
    tonnage = models.IntegerField(null=True, blank=True, verbose_name='注塑机吨位', help_text='注塑机吨位')
    lenght = models.IntegerField(null=True, blank=True, verbose_name='长', help_text='长')
    width = models.IntegerField(null=True, blank=True, verbose_name='宽', help_text='宽')
    height = models.IntegerField(null=True, blank=True, verbose_name='高', help_text='高')
    weight = models.IntegerField(null=True, blank=True, verbose_name='重量', help_text='重量')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-原始模具工作台明细'
        verbose_name_plural = verbose_name
        db_table = 'project_mould_ori_details'

    def __str__(self):
        return str(self.project.name)


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
        (1, '开发构建'),
        (2, '版本变更'),
    )
    name = models.CharField(max_length=60, unique=True, verbose_name='模具名', help_text='模具名')
    mould = models.ForeignKey(MouldVersion, on_delete=models.CASCADE, verbose_name='模具版本', help_text='模具版本')
    ori_mould_project = models.ForeignKey(OriMouldProject, on_delete=models.CASCADE, verbose_name='原始磨具', help_text='原始磨具')

    category = models.SmallIntegerField(choices=CATEGORY_LIST, default=1, verbose_name='类型', help_text='类型')
    group_label = models.CharField(max_length=60, null=True, blank=True, verbose_name='组标签', help_text='组标签')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-模具工作台'
        verbose_name_plural = verbose_name
        db_table = 'project_mould'

    def __str__(self):
        return self.mould.name


class MouldProjectDetails(models.Model):
    LEVEL = (
        (1, 'S'),
        (2, 'A'),
        (3, 'B'),
        (4, 'C'),
    )
    project = models.ForeignKey(MouldProject, on_delete=models.CASCADE, verbose_name='模具项目', help_text='模具项目')
    details = models.ForeignKey(MiddlePartsVersion, on_delete=models.CASCADE, verbose_name='中间件', help_text='中间件')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-模具工作台明细'
        verbose_name_plural = verbose_name
        db_table = 'project_mould_details'

    def __str__(self):
        return str(self.project.name)


class LogOriMouldProject(models.Model):

    objects = models.ForeignKey(OriMouldProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-原始模具工作台-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_mould_ori_logging'

    def __str__(self):
        return self.name


class LogMouldProject(models.Model):

    objects = models.ForeignKey(MouldProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-模具工作台-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_mould_logging'

    def __str__(self):
        return self.name


