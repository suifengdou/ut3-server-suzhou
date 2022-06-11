
from django.db import models
from apps.base.center.models import Center
from apps.supplier.mouldsup.models import MouldSupplier
from apps.supplier.packsup.models import PackSupplier
from apps.bom.units.models import Units
from apps.bom.middleparts.models import MiddlePartsVersion


class Mould(models.Model):

    CATEGORY = (
        (1, 'S'),
        (2, 'A'),
        (3, 'B'),
        (4, 'C'),
    )

    name = models.CharField(max_length=60, unique=True, verbose_name='模具名', help_text='模具名')
    mould_id = models.CharField(max_length=60, unique=True, verbose_name='模具ID', help_text='模具ID')
    cavity_num = models.CharField(max_length=60, null=True, blank=True, verbose_name='模穴数', help_text='模穴数')
    gate_type = models.CharField(max_length=60, null=True, blank=True, verbose_name='浇口类型', help_text='浇口类型')
    cavity_steel = models.CharField(max_length=60, null=True, blank=True, verbose_name='前模钢料', help_text='前模钢料')
    core_steel = models.CharField(max_length=60, null=True, blank=True, verbose_name='后模钢料', help_text='后模钢料')
    difficulty_level = models.SmallIntegerField(choices=CATEGORY, null=True, blank=True, db_index=True, verbose_name='制造困难等级', help_text='制造困难等级')
    mould_supplier = models.ForeignKey(MouldSupplier, on_delete=models.CASCADE, null=True, blank=True,  verbose_name='模具生产商', help_text='模具生产商')
    life_span = models.IntegerField(null=True, blank=True, verbose_name='寿命', help_text='寿命')
    Units = models.ForeignKey(Units, on_delete=models.CASCADE, verbose_name='整机项目', help_text='整机项目')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-模具-模具列表'
        verbose_name_plural = verbose_name
        db_table = 'bom_mould'

    def __str__(self):
        return self.name


class MouldVersion(models.Model):

    name = models.CharField(max_length=60, unique=True, verbose_name='版本号名', help_text='版本号名')
    number = models.IntegerField(null=True, blank=True, verbose_name='版本', help_text='版本')
    version_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='版本编码', help_text='版本编码')
    mould = models.ForeignKey(Mould, on_delete=models.CASCADE, verbose_name='模具', help_text='模具')
    file_name = models.CharField(max_length=60, verbose_name='文件名', help_text='文件名')
    surface = models.CharField(max_length=60, null=True, blank=True, verbose_name='表面处理', help_text='表面处理')
    tonnage = models.IntegerField(null=True, blank=True, verbose_name='注塑机吨位', help_text='注塑机吨位')
    lenght = models.IntegerField(null=True, blank=True, verbose_name='长', help_text='长')
    width = models.IntegerField(null=True, blank=True, verbose_name='宽', help_text='宽')
    height = models.IntegerField(null=True, blank=True, verbose_name='高', help_text='高')
    weight = models.IntegerField(null=True, blank=True, verbose_name='重量', help_text='重量')


    class Meta:
        verbose_name = 'BOM-模具-模具版本'
        unique_together = (("number", "mould"), )
        verbose_name_plural = verbose_name
        db_table = 'bom_mould_version'

    def __str__(self):
        return self.name


class MouldVersionDetails(models.Model):

    name = models.CharField(max_length=60, unique=True, verbose_name='版本号名', help_text='版本号名')
    number = models.IntegerField(null=True, blank=True, verbose_name='版本', help_text='版本')
    version_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='版本编码', help_text='版本编码')
    mould = models.ForeignKey(MouldVersion, on_delete=models.CASCADE, verbose_name='模具版本', help_text='模具版本')
    middle_parts = models.ForeignKey(MiddlePartsVersion, on_delete=models.CASCADE, verbose_name='中间件版本', help_text='中间件版本')
    pack_supplier = models.ForeignKey(PackSupplier, on_delete=models.CASCADE, null=True, blank=True, verbose_name='注塑厂',
                                      help_text='注塑厂')

    class Meta:
        verbose_name = 'BOM-模具-模具版本明细'
        unique_together = (("number", "mould"), )
        verbose_name_plural = verbose_name
        db_table = 'bom_mould_version_details'

    def __str__(self):
        return self.name





