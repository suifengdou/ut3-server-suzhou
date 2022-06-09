
from django.db import models
from apps.bom.material.models import Material
from apps.bom.initialparts.models import PartsCategory
from apps.auth.users.models import UserProfile


class MiddleParts(models.Model):

    name = models.CharField(max_length=90, unique=True, verbose_name='中间件', help_text='中间件')
    units_id = models.CharField(max_length=90, unique=True, verbose_name='中间件编码', help_text='中间件编码')
    category = models.ForeignKey(PartsCategory, on_delete=models.CASCADE, verbose_name='类型', help_text='类型')
    diagram_number = models.IntegerField(null=True, blank=True, verbose_name='爆炸图号', help_text='爆炸图号')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-中间件'
        verbose_name_plural = verbose_name
        db_table = 'bom_middleparts'

    def __str__(self):
        return self.name


class MiddlePartsVersion(models.Model):
    name = models.CharField(max_length=90, unique=True, verbose_name='版本号名', help_text='版本号名')
    number = models.IntegerField(null=True, blank=True, verbose_name='版本', help_text='版本')
    version_id = models.IntegerField(null=True, blank=True, verbose_name='版本编码', help_text='版本编码')
    middleparts = models.ForeignKey(MiddleParts, on_delete=models.CASCADE, verbose_name='中间件', help_text='中间件')
    specification = models.CharField(null=True, blank=True, max_length=160, verbose_name='规格', help_text='规格')

    technology = models.CharField(null=True, blank=True, max_length=160, verbose_name='工艺', help_text='工艺')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='原材料', help_text='原材料')
    Shrinkage = models.CharField(null=True, blank=True, verbose_name='成型收缩率', help_text='成型收缩率')
    material_color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='材料色号', help_text='材料色号')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='用量', help_text='用量')
    weight = models.IntegerField(null=True, blank=True, verbose_name='克重', help_text='克重')

    daily_capacity = models.IntegerField(null=True, blank=True, verbose_name='日产能', help_text='日产能')
    cycle_time = models.IntegerField(null=True, blank=True, verbose_name='成型周期', help_text='成型周期')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-中间件-版本'
        verbose_name_plural = verbose_name
        db_table = 'bom_middleparts_version'

    def __str__(self):
        return self.name


