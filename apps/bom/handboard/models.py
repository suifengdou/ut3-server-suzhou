
from django.db import models
from apps.auth.users.models import UserProfile
from apps.supplier.handboardsup.models import HandBoardSupplier
from apps.bom.subunit.models import SubUnit
from apps.bom.initialparts.models import InitialParts

class HandBoardCategory(models.Model):

    name = models.CharField(max_length=50, unique=True, verbose_name='手板类型', help_text='手板类型')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')
    class Meta:
        verbose_name = 'BOM-手板类型'
        verbose_name_plural = verbose_name
        db_table = 'bom_handboard_category'

    def __str__(self):
        return self.name


class HandBoard(models.Model):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '等待递交'),
        (2, '等待执行'),
        (3, '等待评测'),
        (4, '手板完结')
    )
    name = models.CharField(max_length=50, unique=True, verbose_name='手板名称', help_text='手板名称')
    units_id = models.CharField(max_length=50, unique=True, verbose_name='手板编码', help_text='手板编码')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-手板'
        verbose_name_plural = verbose_name
        db_table = 'bom_handboard'

    def __str__(self):
        return self.name


class HandBoardDetails(models.Model):

    handboard = models.ForeignKey(HandBoard, on_delete=models.CASCADE, verbose_name='手板', help_text='手板')
    name = models.CharField(max_length=50, unique=True, verbose_name='手板名称', help_text='手板名称')
    units_id = models.CharField(max_length=50, unique=True, verbose_name='整机编码', help_text='整机编码')
    handboardsupplier = models.ForeignKey(HandBoardSupplier, on_delete=models.CASCADE, verbose_name='手板供应商', help_text='手板供应商')
    initial_parts = models.ForeignKey(InitialParts, on_delete=models.CASCADE, verbose_name='初始物料', help_text='初始物料')
    is_handboard = models.BooleanField(default=False, verbose_name='是否制板', help_text='是否制板')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-手板明细'
        verbose_name_plural = verbose_name
        db_table = 'bom_handboard_details'

    def __str__(self):
        return self.name


class LogHandBoard(models.Model):

    object = models.ForeignKey(HandBoard, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'BOM-手板日志'
        verbose_name_plural = verbose_name
        db_table = 'bom_handboard_logging'

    def __str__(self):
        return self.name




