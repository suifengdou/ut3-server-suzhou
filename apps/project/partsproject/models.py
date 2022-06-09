
from django.db import models
from apps.bom.middleparts.models import MiddlePartsVersion
from apps.auth.users.models import UserProfile
from apps.bom.parts.models import AtomicPartsVersion
from apps.bom.productline.models import ProductLine
from apps.bom.units.models import UnitsVersion
from apps.bom.component.models import ComponentVersion
from apps.supplier.packsup.models import PackSupplier


class PartsProject(models.Model):
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
    name = models.CharField(max_length=50, unique=True, verbose_name='零配件类型', help_text='零配件类型')
    units_id = models.CharField(max_length=50, unique=True, verbose_name='零配件编码', help_text='零配件编码')
    atomic_parts = models.ForeignKey(AtomicPartsVersion, on_delete=models.CASCADE, verbose_name='原子件', help_text='原子件')

    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, null=True, blank=True, verbose_name='产品线', help_text='产品线')
    units = models.ForeignKey(UnitsVersion, on_delete=models.CASCADE, null=True, blank=True, verbose_name='整机', help_text='整机')
    pack_supplier = models.ForeignKey(PackSupplier, on_delete=models.CASCADE, null=True, blank=True, verbose_name='供应商',
                                      help_text='供应商')
    component = models.ForeignKey(ComponentVersion, on_delete=models.CASCADE, verbose_name='组件', help_text='组件')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='用量', help_text='用量')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-零配件工作台'
        verbose_name_plural = verbose_name
        db_table = 'project_parts'

    def __str__(self):
        return self.name


class LogPartsProject(models.Model):
    object = models.ForeignKey(PartsProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-零配件工作台日志'
        verbose_name_plural = verbose_name
        db_table = 'project_parts_logging'

    def __str__(self):
        return self.name


