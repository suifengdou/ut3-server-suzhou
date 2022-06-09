
from django.db import models
from apps.bom.productline.models import ProductLine
from apps.utils.geography.models import Nationality
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.bom.subunit.models import SubUnitVersion


class SubUnitProject(models.Model):

    name = models.CharField(max_length=50, unique=True, verbose_name='子项目名称', help_text='子项目名称')
    subunits_id = models.CharField(max_length=50, unique=True, verbose_name='子项目编码', help_text='子项目编码')
    subunits_version =  models.ForeignKey(SubUnitVersion, null=True, blank=True, on_delete=models.CASCADE, verbose_name='子项目版本', help_text='子项目版本')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'OM-整机'
        verbose_name_plural = verbose_name
        db_table = 'bom_units'

    def __str__(self):
        return self.name


class SubUnitsDetails(models.Model):

    unit_project = models.ForeignKey(SubUnitProject, on_delete=models.CASCADE, verbose_name='项目', help_text='项目')
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