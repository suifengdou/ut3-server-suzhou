
from django.db import models
from apps.auth.users.models import UserProfile
from apps.bom.parts.models import AtomicPartsVersion
from apps.bom.bom.models import BOM, BOMVersion
from apps.bom.units.models import Units


class Payment(models.Model):

    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '等待递交'),
        (2, '等待处理'),
        (3, '等待执行'),
        (4, '终审复核'),
        (5, '财务审核'),
        (6, '工单完结')
    )
    CATEGORY = (
        (1, '新项目'),
        (2, '改项目'),
        (3, '改单件'),
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
    units_id = models.CharField(max_length=50, unique=True, verbose_name='付款单编码', help_text='付款单编码')
    order_category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='付款类型', help_text='付款类型')

    bom = models.OneToOneField(BOM, on_delete=models.CASCADE, verbose_name='BOM', help_text='BOM')
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
        return self.name
