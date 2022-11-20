from django.db import models
from apps.bom.productline.models import ProductLine
from apps.utils.geography.models import Nationality
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.bom.subunit.models import SubUnitVersion
from apps.bom.component.models import ComponentVersion
from apps.project.phototypeexecuteproject.models import PhototypeExecuteProject
from apps.bom.initialparts.models import InitialParts

from apps.supplier.phototypesupplier.models import PhototypeSupplier


class PhototypeExecuteProjectStatement(models.Model):

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
        (1, '未标记单据不可审核'),
        (2, '已拆分或者结算金额为零的订单不可用全额创建'),
        (3, '付款单关联关系错误，请联系管理员'),
        (4, '付款单创建失败'),
        (5, '付款关联关系单创建失败'),
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
    name = models.CharField(max_length=50, unique=True, verbose_name='手板结算单名', help_text='手板结算单名')
    code = models.CharField(max_length=50, unique=True, verbose_name='手板结算号', help_text='手板结算号')
    project = models.OneToOneField(PhototypeExecuteProject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='原单', help_text='原单')
    supplier = models.ForeignKey(PhototypeSupplier, on_delete=models.CASCADE, verbose_name='供应商', help_text='供应商')
    amount = models.FloatField(default=0, verbose_name='金额', help_text='总金额')
    adjust_amount = models.FloatField(default=0, verbose_name='调整金额', help_text='调整金额')
    settle_amount = models.FloatField(default=0, verbose_name='结算金额', help_text='结算金额')
    remaining = models.FloatField(default=0, verbose_name='未结算金额', help_text='未结算金额')
    is_making = models.BooleanField(default=False, verbose_name='是否制板', help_text='是否制板')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'STATEMENT-手板执行结算单'
        verbose_name_plural = verbose_name
        db_table = 'statement_phototype_execute'

    def __str__(self):
        return str(self.id)


class LogPhototypeExecuteProjectStatement(models.Model):

    obj = models.ForeignKey(PhototypeExecuteProjectStatement, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'STATEMENT-手板执行结算单-日志'
        verbose_name_plural = verbose_name
        db_table = 'statement_phototype_execute_logging'

    def __str__(self):
        return str(self.id)

