from django.db import models
from apps.base.company.models import Company
import django.utils.timezone as timezone
import pandas as pd


class MouldSupplier(models.Model):
    LEVEL_LIST = (
        (0, '无'),
        (1, 'S'),
        (2, 'A'),
        (3, 'B'),
        (4, 'C'),
    )
    ORDER_STATUS = (
        (0, '未合作'),
        (1, '合作中'),
        (2, '解除合作'),
    )

    name = models.CharField(unique=True, max_length=30, verbose_name='模具商', db_index=True, help_text='模具商')
    company = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name='公司', help_text='公司')
    level = models.IntegerField(choices=LEVEL_LIST, default=0, verbose_name='级别', help_text='级别')
    order_status = models.IntegerField(choices=ORDER_STATUS, default=0, verbose_name='状态', help_text='状态')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'SUPPLIER-手板'
        verbose_name_plural = verbose_name
        db_table = 'supplier_mould'

    def __str__(self):
        return self.name

