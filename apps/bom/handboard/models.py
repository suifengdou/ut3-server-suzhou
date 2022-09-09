
from django.db import models
from apps.auth.users.models import UserProfile
from apps.supplier.handboardsup.models import HandBoardSupplier
from apps.bom.subunit.models import SubUnit
from apps.bom.component.models import Component
from apps.bom.initialparts.models import InitialParts


class HandBoard(models.Model):
    CATEGORY_LIST = (
        (1, '外观'),
        (2, '结构'),
        (3, '功能'),
    )
    name = models.CharField(max_length=50, unique=True, verbose_name='手板名称', help_text='手板名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='手板编码', help_text='手板编码')
    category = models.SmallIntegerField(choices=CATEGORY_LIST, default=1, verbose_name='类型', help_text='类型')
    subunit = models.ForeignKey(SubUnit, on_delete=models.CASCADE, verbose_name='子项', help_text='子项')
    is_component = models.BooleanField(default=False, verbose_name='是否组项', help_text='是否组项')
    component = models.ForeignKey(Component, on_delete=models.CASCADE, null=True, blank=True, verbose_name='组项', help_text='组项')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者',
                                help_text='创建者')

    class Meta:
        verbose_name = 'BOM-手板'
        verbose_name_plural = verbose_name
        db_table = 'bom_handboard'

    def __str__(self):
        return self.name


class HandBoardDetails(models.Model):

    handboard = models.ForeignKey(HandBoard, on_delete=models.CASCADE, verbose_name='手板', help_text='手板')
    handboardsupplier = models.ForeignKey(HandBoardSupplier, on_delete=models.CASCADE, verbose_name='手板供应商', help_text='手板供应商')
    initial_parts = models.ForeignKey(InitialParts, on_delete=models.CASCADE, verbose_name='初始物料', help_text='初始物料')
    is_handboard = models.BooleanField(default=False, verbose_name='是否制板', help_text='是否制板')
    quantity = models.IntegerField(default=1, verbose_name='数量', help_text='数量')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者',
                                help_text='创建者')

    class Meta:
        verbose_name = 'BOM-手板明细'
        verbose_name_plural = verbose_name
        db_table = 'bom_handboard_details'

    def __str__(self):
        return self.initial_parts.name


