from django.db import models
import django.utils.timezone as timezone
import pandas as pd
from apps.auth.users.models import UserProfile


class PLCategory(models.Model):
    name = models.CharField(unique=True, max_length=30, verbose_name='系列类型', db_index=True, help_text='系列类型')
    code = models.CharField(unique=True, max_length=30, verbose_name='类型代码', db_index=True, help_text='类型代码')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-系列-类型'
        verbose_name_plural = verbose_name
        db_table = 'bom_productline_category'

    def __str__(self):
        return self.name


class ProductLine(models.Model):

    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '等待命名'),
        (2, '命名完成'),
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

    name = models.CharField(unique=True, max_length=30, verbose_name='系列名称', db_index=True, help_text='系列名称')
    code = models.CharField(unique=True, max_length=30, verbose_name='系列编码', db_index=True, help_text='系列编码')
    category = models.ForeignKey(PLCategory, on_delete=models.CASCADE, verbose_name='系列类型', help_text='系列类型')
    is_named = models.BooleanField(default=False, verbose_name='是否命名', help_text='是否命名')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='状态', help_text='状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-系列'
        verbose_name_plural = verbose_name
        db_table = 'bom_productline'

    def __str__(self):
        return self.name
