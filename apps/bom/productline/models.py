from django.db import models
import django.utils.timezone as timezone
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.bom.component.models import ComponentCategory


class PLCategory(models.Model):
    name = models.CharField(unique=True, max_length=30, verbose_name='系列类型', db_index=True, help_text='系列类型')
    pl_id = models.CharField(unique=True, max_length=30, verbose_name='类型代码', db_index=True, help_text='类型代码')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-系列-类型'
        verbose_name_plural = verbose_name
        db_table = 'bom_productline_category'

    def __str__(self):
        return self.name


class ProductLine(models.Model):

    name = models.CharField(unique=True, max_length=30, verbose_name='系列名称', db_index=True, help_text='系列名称')
    line_id = models.CharField(unique=True, max_length=30, verbose_name='系列ID', db_index=True, help_text='系列ID')
    category = models.ForeignKey(PLCategory, on_delete=models.CASCADE, verbose_name='系列类型', help_text='系列类型')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-系列'
        verbose_name_plural = verbose_name
        db_table = 'bom_productline'

    def __str__(self):
        return self.name


class ProductLineListProject(models.Model):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '等待递交'),
        (2, '等待处理'),
        (3, '等待执行'),
        (4, '终审复核'),
        (5, '财务审核'),
        (6, '工单完结')
    )
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, verbose_name='产品线', help_text='产品线')
    component_category = models.ForeignKey(ComponentCategory, on_delete=models.CASCADE, verbose_name='组件类型名', help_text='组件类型名')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-产品线-组件列表'
        verbose_name_plural = verbose_name
        db_table = 'project_product_line_list'

    def __str__(self):
        return str(self.product_line.name)


class LogProductLineListProject(models.Model):

    objects = models.ForeignKey(ProductLineListProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-产品线-组件列表-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_product_line_list_logging'

    def __str__(self):
        return self.name
