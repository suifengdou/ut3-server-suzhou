from django.db import models
from apps.bom.material.models import Material
from apps.auth.users.models import UserProfile
from apps.bom.initialparts.models import PartsCategory
from apps.bom.subunit.models import SubUnitVersion
from apps.bom.units.models import UnitsVersion
from apps.bom.component.models import ComponentVersion



class IPWorkbench(models.Model):

    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '等待递交'),
        (2, '等待执行'),
        (3, '等待评测'),
        (4, '手板完结')
    )

    name = models.CharField(max_length=90, unique=True, verbose_name='名称', help_text='名称')
    units_id = models.CharField(max_length=90, unique=True, verbose_name='编码', help_text='编码')

    units_version = models.ForeignKey(UnitsVersion, on_delete=models.CASCADE, verbose_name='整机项目版本', help_text='整机项目版本')
    subunit_version = models.ForeignKey(UnitsVersion, on_delete=models.CASCADE, verbose_name='子项目版本', help_text='子项目版本')
    component_version = models.ForeignKey(ComponentVersion, on_delete=models.CASCADE, verbose_name='组项目版本', help_text='组项目版本')
    group_number = models.IntegerField(null=True, blank=True, verbose_name='分组号', help_text='分组号')
    category = models.ForeignKey(PartsCategory, on_delete=models.CASCADE, verbose_name='类型', help_text='类型')
    diagram_number = models.IntegerField(null=True, blank=True, verbose_name='爆炸图号', help_text='爆炸图号')

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

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态', help_text='单据状态')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'HB-初始物料工作台'
        verbose_name_plural = verbose_name
        db_table = 'bom_initialparts'

    def __str__(self):
        return self.name


class LogHandBoard(models.Model):
    object = models.ForeignKey(IPWorkbench, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'HB-手板日志'
        verbose_name_plural = verbose_name
        db_table = 'hb_handboard_logging'

    def __str__(self):
        return self.name
