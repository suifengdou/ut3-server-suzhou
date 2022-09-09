
from django.db import models
from apps.auth.users.models import UserProfile


class ComponentCategory(models.Model):
    TYPE_LIST = (
        (1, '主机'),
        (2, '附件'),
    )

    name = models.CharField(max_length=100, unique=True, verbose_name='组项类型名', help_text='组项目类型名')
    code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='组项类型编码', help_text='组项目类型编码')
    type = models.IntegerField(choices=TYPE_LIST, default=1, verbose_name='子项类别', help_text='子项类别')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-组项-类别'
        verbose_name_plural = verbose_name
        db_table = 'bom_component_category'

    def __str__(self):
        return self.name


class Component(models.Model):

    name = models.CharField(max_length=100, unique=True, verbose_name='组项', help_text='组项')
    code = models.CharField(max_length=50, unique=True, verbose_name='组项编码', help_text='组项编码')
    category = models.ForeignKey(ComponentCategory, on_delete=models.CASCADE, verbose_name='类型', help_text='类型')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-组项'
        verbose_name_plural = verbose_name
        db_table = 'bom_component'

    def __str__(self):
        return self.name


class ComponentVersion(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name='版本号名', help_text='版本号名')
    number = models.IntegerField(null=True, blank=True, verbose_name='版本', help_text='版本')
    code = models.CharField(null=True, blank=True, unique=True, max_length=60, verbose_name='版本编码', help_text='版本编码')
    component = models.ForeignKey(Component, on_delete=models.CASCADE, verbose_name='组项', help_text='组项')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-组项版本'
        verbose_name_plural = verbose_name
        db_table = 'bom_component_version'

    def __str__(self):
        return self.name



#

