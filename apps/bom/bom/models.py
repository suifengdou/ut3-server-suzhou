
from django.db import models
from apps.bom.goods.models import AtomicPartsVersion
from apps.auth.users.models import UserProfile
from apps.bom.units.models import UnitsVersion


class BOM(models.Model):

    name = models.CharField(max_length=50, unique=True, verbose_name='BOM', help_text='BOM')
    code = models.CharField(max_length=50, unique=True, verbose_name='BOM编码', help_text='BOM编码')
    units = models.OneToOneField(UnitsVersion, on_delete=models.CASCADE, verbose_name='整机', help_text='整机')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'BOM-物料清单'
        verbose_name_plural = verbose_name
        db_table = 'bom_bom'

    def __str__(self):
        return self.name


class BOMDetails(models.Model):
    version = models.ForeignKey(BOM, on_delete=models.CASCADE, verbose_name='BOM', help_text='BOM')
    details = models.ForeignKey(AtomicPartsVersion, on_delete=models.CASCADE, verbose_name='原子件', help_text='原子件')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='数量', help_text='数量')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'BOM-物料清单明细'
        verbose_name_plural = verbose_name
        db_table = 'bom_bom_details'

    def __str__(self):
        return self.details.name

