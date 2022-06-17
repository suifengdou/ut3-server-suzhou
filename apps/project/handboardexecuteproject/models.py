
from django.db import models
from apps.bom.productline.models import ProductLine
from apps.utils.geography.models import Nationality
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.bom.subunit.models import SubUnitVersion
from apps.bom.component.models import ComponentVersion
from apps.bom.handboard.models import HandBoard
from apps.bom.initialparts.models import InitialParts
from apps.supplier.handboardsup.models import HandBoardSupplier


class HandBoardExecuteProject(models.Model):

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
    name = models.CharField(max_length=50, unique=True, verbose_name='手板执行单名称', help_text='手板执行单名称')
    units_id = models.CharField(max_length=50, unique=True, verbose_name='手板编码', help_text='手板编码')
    handboard = models.ForeignKey(HandBoard, on_delete=models.CASCADE, null=True, blank=True, verbose_name='手板', help_text='手板')
    supplier = models.ForeignKey(HandBoardSupplier, on_delete=models.CASCADE, verbose_name='供应商', help_text='供应商')
    quantity = models.IntegerField(default=0, verbose_name='总数量', help_text='总数量')
    amount = models.FloatField(default=0, verbose_name='金额', help_text='总金额')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-手板项目执行单'
        verbose_name_plural = verbose_name
        db_table = 'project_handboard_execute'

    def __str__(self):
        return self.name


class HandBoardExecuteProjectDetails(models.Model):

    handboard = models.ForeignKey(HandBoardExecuteProject, on_delete=models.CASCADE, verbose_name='手板执行单', help_text='手板执行单')
    name = models.CharField(max_length=50, unique=True, verbose_name='手板名称', help_text='手板名称')
    units_id = models.CharField(max_length=50, unique=True, verbose_name='整机编码', help_text='整机编码')
    initial_parts = models.ForeignKey(InitialParts, on_delete=models.CASCADE, verbose_name='初始物料', help_text='初始物料')
    group_number = models.CharField(null=True, blank=True, max_length=30, verbose_name='组编号', help_text='组编号')
    quantity = models.IntegerField(default=0, verbose_name='数量', help_text='数量')
    price = models.FloatField(default=0, verbose_name='单价', help_text='单价')
    amount = models.FloatField(default=0, verbose_name='合计金额', help_text='合计金额')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-手板项目执行单明细'
        verbose_name_plural = verbose_name
        db_table = 'project_handboard_execute_details'

    def __str__(self):
        return self.name


class LogHandBoardExecuteProject(models.Model):
    object = models.ForeignKey(HandBoardExecuteProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-手板项目执行单日志'
        verbose_name_plural = verbose_name
        db_table = 'project_handboard_execute_logging'

    def __str__(self):
        return self.name
