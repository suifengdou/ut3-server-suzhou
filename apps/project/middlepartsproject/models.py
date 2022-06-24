
from django.db import models
from apps.auth.users.models import UserProfile

from apps.bom.middleparts.models import MiddlePartsVersion
from apps.supplier.packsup.models import PackSupplier
from apps.bom.component.models import ComponentVersion
from apps.bom.units.models import UnitsVersion
from apps.bom.productline.models import ProductLine


class MiddlePartsProject(models.Model):

    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '等待递交'),
        (2, '等待处理'),
        (3, '等待执行'),
        (4, '终审复核'),
        (5, '财务审核'),
        (6, '工单完结')
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '快递单号错误'),
        (2, '处理意见为空'),
        (3, '返回的单据无返回单号'),
        (4, '理赔必须设置需理赔才可以审核'),
        (5, '驳回原因为空'),
        (6, '无反馈内容, 不可以审核'),
    )
    PROCESSTAG = (
        (0, '未分类'),
        (1, '待截单'),
        (2, '签复核'),
        (3, '改地址'),
        (4, '催派查'),
        (5, '丢件核'),
        (6, '纠纷中'),
        (7, '需理赔'),
        (8, '其他类'),
    )

    CATEGORY_LIST = (
        (1, '开发构建'),
        (2, '版本变更'),
    )
    category = models.SmallIntegerField(choices=CATEGORY_LIST, default=1, verbose_name='类型', help_text='类型')

    name = models.CharField(max_length=90, unique=True, verbose_name='中间件', help_text='中间件')
    units_id = models.CharField(max_length=90, unique=True, verbose_name='中间件编码', help_text='中间件编码')
    middleparts = models.ForeignKey(MiddlePartsVersion, on_delete=models.CASCADE, verbose_name='中间件', help_text='中间件')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, null=True, blank=True, verbose_name='产品线', help_text='产品线')
    units = models.ForeignKey(UnitsVersion, on_delete=models.CASCADE, null=True, blank=True, verbose_name='整机项目', help_text='整机项目')
    pack_supplier = models.ForeignKey(PackSupplier, on_delete=models.CASCADE, null=True, blank=True, verbose_name='供应商', help_text='供应商')
    component = models.ForeignKey(ComponentVersion, on_delete=models.CASCADE, verbose_name='组件', help_text='组件')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='用量', help_text='用量')
    is_lacquered = models.BooleanField(default=False, verbose_name='是否喷漆', help_text='是否喷漆')
    lacquer_color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='色号', help_text='色号')
    craft_content = models.CharField(null=True, blank=True, max_length=200, verbose_name='工艺内容', help_text='工艺内容')

    is_cell = models.BooleanField(default=False, verbose_name='是否单元', help_text='是否单元')
    cell_name = models.CharField(null=True, blank=True, max_length=90, verbose_name='单元名', help_text='单元名')
    cell_number = models.IntegerField(default=0, verbose_name='单元序号', help_text='单元序号')

    is_kit = models.BooleanField(default=False, verbose_name='是否套件', help_text='是否套件')
    kit_name = models.CharField(null=True, blank=True, max_length=90, verbose_name='套件名', help_text='套件名')
    kit_number = models.IntegerField(default=0, verbose_name='套件序号', help_text='套件序号')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-中间件工作台'
        verbose_name_plural = verbose_name
        db_table = 'project_middleparts'

    def __str__(self):
        return self.name


class LogMiddlePartsProject(models.Model):
    object = models.ForeignKey(MiddlePartsProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-中间件工作台日志'
        verbose_name_plural = verbose_name
        db_table = 'project_middleparts_logging'

    def __str__(self):
        return self.name


