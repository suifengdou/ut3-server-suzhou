
from django.db import models
from apps.bom.productline.models import ProductLine
from apps.utils.geography.models import Nationality
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.bom.subunit.models import SubUnitVersion

class Units(models.Model):

    name = models.CharField(max_length=50, unique=True, verbose_name='整机', help_text='整机')
    units_id = models.CharField(max_length=50, unique=True, verbose_name='整机编码', help_text='整机编码')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, verbose_name='产品线', help_text='产品线')
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, verbose_name='国别', help_text='国别')
    serial_number = models.IntegerField(null=True, blank=True, unique=True, verbose_name='系列排序', help_text='系列排序')
    unit_number = models.IntegerField(null=True, blank=True, unique=True, verbose_name='整机排序', help_text='整机排序')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-整机'
        verbose_name_plural = verbose_name
        db_table = 'bom_units'

    def __str__(self):
        return self.name


class UnitsVersion(models.Model):

    name = models.CharField(max_length=60, unique=True, verbose_name='版本号名', help_text='版本号名')
    number = models.IntegerField(null=True, blank=True, verbose_name='版本', help_text='版本')
    version_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='版本编码', help_text='版本编码')
    units = models.ForeignKey(Units, on_delete=models.CASCADE, verbose_name='整机', help_text='整机')

    is_default = models.BooleanField(default=False, verbose_name="是否默认", help_text="是否默认")
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-整机版本'
        verbose_name_plural = verbose_name
        db_table = 'bom_units_version'

    def __str__(self):
        return self.name


class UnitsVersionDetails(models.Model):

    version = models.ForeignKey(UnitsVersion, on_delete=models.CASCADE, verbose_name='整机', help_text='整机')
    details = models.ForeignKey(SubUnitVersion, on_delete=models.CASCADE, verbose_name='子项版本', help_text='子项版本')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-整机版本明细'
        verbose_name_plural = verbose_name
        unique_together = (("units_version", "subunit_version"),)
        db_table = 'bom_units_version_details'

    def __str__(self):
        return str(self.version.name)


class LogUnits(models.Model):

    object = models.ForeignKey(Units, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'BOM-整机-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_mpworkbench_logging'

    def __str__(self):
        return self.name


