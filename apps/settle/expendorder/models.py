
from django.db import models
from apps.auth.users.models import UserProfile
from apps.bom.bom.models import BOM
from apps.bom.units.models import Units
from apps.settle.payment.models import PaymentOrder
from apps.base.company.models import Company


class ExpendOrder(models.Model):

    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待递交'),
        (2, '已支付'),
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

    name = models.CharField(max_length=50, unique=True, verbose_name='付款单名称', help_text='付款单名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='付款流水号', help_text='付款流水号')
    bank_name = models.CharField(max_length=50, verbose_name='付款方式', help_text='付款方式')
    supplier = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='供应商', help_text='供应商')
    account = models.CharField(null=True, blank=True, max_length=100, verbose_name='收款账号', help_text='收款账号')
    payment_order = models.ForeignKey(PaymentOrder, on_delete=models.CASCADE, verbose_name='付款单', help_text='付款单')
    paid_amount = models.FloatField(default=0, verbose_name='已付金额', help_text='已付金额')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'SETTLE-支付单'
        verbose_name_plural = verbose_name
        db_table = 'settle_expend'

    def __str__(self):
        return str(self.id)


class ExpendOrderDetails(models.Model):

    expend = models.ForeignKey(ExpendOrder, on_delete=models.CASCADE, verbose_name='支付单', help_text='供应商')
    payment = models.ForeignKey(PaymentOrder, on_delete=models.CASCADE, verbose_name='付款单', help_text='供应商')
    paid_amount = models.FloatField(default=0, verbose_name='分配金额', help_text='分配金额')

    class Meta:
        verbose_name = 'SETTLE-支付单明细'
        verbose_name_plural = verbose_name
        db_table = 'settle_expend_details'

    def __str__(self):
        return str(self.id)


class LogExpendOrder(models.Model):

    obj = models.ForeignKey(ExpendOrder, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'SETTLE-付款单-日志'
        verbose_name_plural = verbose_name
        db_table = 'settle_expend_logging'

    def __str__(self):
        return str(self.id)


class ExpendOrderFiles(models.Model):

    name = models.CharField(max_length=150, verbose_name='文件名称', help_text='文件名称')
    suffix = models.CharField(max_length=100, verbose_name='文件类型', help_text='文件类型')
    url = models.CharField(max_length=250, verbose_name='URL地址', help_text='URL地址')
    workorder = models.ForeignKey(ExpendOrder, on_delete=models.CASCADE, verbose_name='子项项目', help_text='子项项目')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'SETTLE-付款单-文档'
        verbose_name_plural = verbose_name
        db_table = 'settle_expend_files'

    def __str__(self):
        return str(self.id)


