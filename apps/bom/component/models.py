
from django.db import models
from apps.bom.middleparts.models import MiddlePartsVersion
from apps.bom.productline.models import PLCategory
from apps.auth.users.models import UserProfile


class ComponentCategory(models.Model):
    CATEGORY_LIST = (
        (1, '主机'),
        (2, '附件'),
    )

    name = models.CharField(max_length=100, unique=True, verbose_name='组项目类型名', help_text='组项目类型名')
    conponent_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='组项目类型编码', help_text='组项目类型编码')
    productline_category = models.ForeignKey(PLCategory, on_delete=models.CASCADE, verbose_name='系列类型', help_text='系列类型')
    subunit_category = models.IntegerField(choices=CATEGORY_LIST, default=1, verbose_name='子项目类别', help_text='子项目类别')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-组项目-类别'
        verbose_name_plural = verbose_name
        db_table = 'bom_component_category'

    def __str__(self):
        return self.name


class Component(models.Model):

    name = models.CharField(max_length=100, unique=True, verbose_name='组项目', help_text='组项目')
    conponent_id = models.CharField(max_length=50, unique=True, verbose_name='组项目编码', help_text='组项目编码')
    category = models.ForeignKey(ComponentCategory, on_delete=models.CASCADE, verbose_name='类型', help_text='类型')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-组项目'
        verbose_name_plural = verbose_name
        db_table = 'bom_component'

    def __str__(self):
        return self.name


class ComponentVersion(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name='版本号名', help_text='版本号名')
    number = models.IntegerField(null=True, blank=True, verbose_name='版本', help_text='版本')
    version_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='版本编码', help_text='版本编码')
    component = models.ForeignKey(Component, on_delete=models.CASCADE, verbose_name='组项目', help_text='组项目')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-组项目版本'
        verbose_name_plural = verbose_name
        db_table = 'bom_component_version'

    def __str__(self):
        return self.name


class ComponentDetails(models.Model):

    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '等待递交'),
        (2, '等待处理'),
        (3, '等待执行'),
        (4, '终审复核'),
        (5, '财务审核'),
        (6, '工单完结')
    )

    version = models.ForeignKey(ComponentVersion, on_delete=models.CASCADE, verbose_name='组项目', help_text='组项目')
    details = models.ForeignKey(MiddlePartsVersion, on_delete=models.CASCADE, verbose_name='中间件', help_text='中间件')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-组项目明细'
        verbose_name_plural = verbose_name
        db_table = 'bom_component_version_details'

    def __str__(self):
        return self.name