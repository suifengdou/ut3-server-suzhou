
from django.db import models
from apps.bom.productline.models import ProductLine
from apps.utils.geography.models import Nationality
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.bom.subunit.models import SubUnitVersion
from apps.bom.component.models import ComponentVersion
from apps.bom.units.models import UnitsVersion
from apps.bom.initialparts.models import InitialParts


class FaultUnits(models.Model):
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
    LEVEL_LIST = (
        (0, '无'),
        (1, 'C'),
        (2, 'B'),
        (3, 'A'),
        (4, 'S'),
    )
    name = models.CharField(max_length=50, unique=True, verbose_name='问题名称', help_text='问题名称')
    fault_id = models.CharField(max_length=50, unique=True, verbose_name='手板问题单ID', help_text='手板问题单ID')
    object = models.ForeignKey(UnitsVersion, on_delete=models.CASCADE, verbose_name='整机版本', help_text='整机版本')
    level = models.SmallIntegerField(choices=LEVEL_LIST, default=0, verbose_name='问题级别', help_text='问题级别')
    content = models.TextField(null=True, blank=True, verbose_name='问题内容', help_text='问题内容')

    suggestion = models.TextField(null=True, blank=True, verbose_name='处理意见', help_text='处理意见')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间', help_text='处理时间')
    handler = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='handler', verbose_name='处理人', help_text='处理人')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'FAULT-整机问题单'
        verbose_name_plural = verbose_name
        db_table = 'project_units'

    def __str__(self):
        return self.name


