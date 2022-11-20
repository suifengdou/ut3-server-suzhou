
from django.db import models
from apps.auth.users.models import UserProfile
from apps.bom.bom.models import BOM
from apps.bom.units.models import Units
from apps.statement.phototypestatement.models import PhototypeExecuteProjectStatement
from apps.base.company.models import Company


class PaymentOrder(models.Model):

    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待递交'),
        (2, '待支付'),
        (3, '部分支付'),
        (4, '已支付'),
    )
    CATEGORY = (
        (1, '手板付款单'),
        (2, '模具付款单'),
        (3, '订单付款单'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '未标记单据不可确认'),
        (2, '手板付款单约束单错误，请联系管理员'),
        (3, '关联结算单状态必须是待审核，其他状态无法驳回'),
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
    code = models.CharField(max_length=50, unique=True, verbose_name='付款单编码', help_text='付款单编码')
    supplier = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='供应商', help_text='供应商')
    category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='来源类型', help_text='来源类型')
    oa_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='OA编号', help_text='OA编号')
    pay_amount = models.FloatField(default=0, verbose_name='付款金额', help_text='付款金额')
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
        verbose_name = 'SETTLE-付款单'
        verbose_name_plural = verbose_name
        db_table = 'settle_payment'

    def __str__(self):
        return str(self.id)


class RelationPEPSToPay(models.Model):
    """
    手板结算单关联约束model。
    解决无法直接关联付款单的问题。
    """
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待支付'),
        (2, '已支付'),
    )
    CATEGORY = (
        (1, '正向约束'),
        (2, '逆向约束'),
    )
    origin_obj = models.ForeignKey(PhototypeExecuteProjectStatement, on_delete=models.CASCADE, verbose_name='源单据', help_text='源单据')
    origin_amount = models.FloatField(default=0, verbose_name='源单金额', help_text='源单金额')
    pay_obj = models.ForeignKey(PaymentOrder, on_delete=models.CASCADE, verbose_name='付款单', help_text='付款单')
    pay_amount = models.FloatField(default=0, verbose_name='付款金额', help_text='付款金额')
    category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='约束类型', help_text='约束类型')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'SETTLE-手板付款单约束单'
        verbose_name_plural = verbose_name
        db_table = 'settle_payment_peps'

    def __str__(self):
        return str(self.id)


class LogPaymentOrder(models.Model):

    obj = models.ForeignKey(PaymentOrder, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'SETTLE-付款单-日志'
        verbose_name_plural = verbose_name
        db_table = 'settle_payment_logging'

    def __str__(self):
        return str(self.id)


class LogRelationPEPSToPay(models.Model):

    obj = models.ForeignKey(RelationPEPSToPay, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'SETTLE-手板付款单约束单-日志'
        verbose_name_plural = verbose_name
        db_table = 'settle_payment_peps_logging'

    def __str__(self):
        return str(self.id)


class PaymentOrderFiles(models.Model):

    name = models.CharField(max_length=150, verbose_name='文件名称', help_text='文件名称')
    suffix = models.CharField(max_length=100, verbose_name='文件类型', help_text='文件类型')
    url = models.CharField(max_length=250, verbose_name='URL地址', help_text='URL地址')
    workorder = models.ForeignKey(PaymentOrder, on_delete=models.CASCADE, verbose_name='子项项目', help_text='子项项目')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'SETTLE-付款单-文档'
        verbose_name_plural = verbose_name
        db_table = 'settle_payment_files'

    def __str__(self):
        return str(self.id)


