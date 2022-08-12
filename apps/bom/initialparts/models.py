
from django.db import models
from apps.bom.material.models import Material
from apps.auth.users.models import UserProfile


class PartsCategory(models.Model):
    name = models.CharField(unique=True, max_length=30, verbose_name='物料类型', db_index=True, help_text='物料类型')
    code = models.CharField(unique=True, max_length=30, verbose_name='类型代码', db_index=True, help_text='类型代码')
    is_cost = models.BooleanField(default=False, verbose_name='是否成本', help_text='是否成本')
    is_standard = models.BooleanField(default=False, verbose_name='是否标准件', help_text='是否标准件')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-初始物料-类型'
        verbose_name_plural = verbose_name
        db_table = 'bom_initialparts_category'

    def __str__(self):
        return self.name


class InitialParts(models.Model):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待评审'),
        (2, '已评审')
    )

    name = models.CharField(max_length=90, unique=True, verbose_name='初始物料', help_text='初始物料')
    code = models.CharField(max_length=90, unique=True, verbose_name='初始物料编码', help_text='初始物料编码')
    category = models.ForeignKey(PartsCategory, on_delete=models.CASCADE, verbose_name='类型', help_text='类型')
    diagram_number = models.IntegerField(null=True, blank=True, verbose_name='爆炸图号', help_text='爆炸图号')

    specification = models.CharField(null=True, blank=True, max_length=160, verbose_name='规格', help_text='规格')
    technology = models.CharField(null=True, blank=True, max_length=160, verbose_name='工艺', help_text='工艺')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, verbose_name='原材料', help_text='原材料')

    material_color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='材料色号', help_text='材料色号')
    weight = models.IntegerField(null=True, blank=True, verbose_name='克重', help_text='克重')

    is_lacquered = models.BooleanField(default=False, verbose_name='是否喷漆', help_text='是否喷漆')
    color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='色号', help_text='色号')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='状态', help_text='工单状态')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-初始物料'
        verbose_name_plural = verbose_name
        db_table = 'bom_initialparts'

    def __str__(self):
        return self.name

