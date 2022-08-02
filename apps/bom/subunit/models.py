
from django.db import models
from apps.auth.users.models import UserProfile

class SubUnit(models.Model):
    CATEGORY_LIST = (
        (1, '主机'),
        (2, '附件'),
    )
    name = models.CharField(max_length=50, unique=True, verbose_name='子项目', help_text='子项目')
    units_id = models.CharField(max_length=50, unique=True, verbose_name='子项目编码', help_text='子项目编码')

    category = models.IntegerField(choices=CATEGORY_LIST, default=1, verbose_name='子项目类别', help_text='子项目类别')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'BOM-子项目'
        verbose_name_plural = verbose_name
        db_table = 'bom_subunit'

    def __str__(self):
        return self.name


class SubUnitVersion(models.Model):

    name = models.CharField(max_length=60, unique=True, verbose_name='版本号名', help_text='版本号名')
    number = models.IntegerField(null=True, blank=True, verbose_name='版本', help_text='版本')
    version_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='版本编码', help_text='版本编码')
    subunit = models.ForeignKey(SubUnit, on_delete=models.CASCADE, verbose_name='子项', help_text='子项')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'BOM-子项目版本'
        verbose_name_plural = verbose_name
        db_table = 'bom_subunit_version'

    def __str__(self):
        return self.name


