from django.db import models
from apps.bom.productline.models import ProductLine
from apps.utils.geography.models import Nationality
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.base.company.models import Company


class ContractCategory(models.Model):

    name = models.CharField(max_length=50, unique=True, verbose_name='零配件类型', help_text='零配件类型')
    units_id = models.CharField(max_length=50, unique=True, verbose_name='零配件编码', help_text='零配件编码')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PURCHASE-合同类型'
        verbose_name_plural = verbose_name
        db_table = 'purchase_contract_category'

    def __str__(self):
        return self.name


class Contract(models.Model):
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
    TYPE_LIST = (
        (1, '新签'),
        (2, '续签'),
    )

    name = models.CharField(max_length=50, verbose_name='合同名称', help_text='合同名称')
    contract_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='合同编码', help_text='合同编码')
    first_party =  models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name='first_party', verbose_name='甲方公司', help_text='甲方公司')
    second_party =  models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name='second_party', verbose_name='乙方公司', help_text='乙方公司')
    category = models.ForeignKey(ContractCategory, null=True, blank=True, on_delete=models.CASCADE, verbose_name='类型', help_text='类型')
    expire_time = models.DateTimeField(verbose_name='到期时间', help_text='到期时间')
    is_renew = models.BooleanField(default=False, verbose_name='到期是否续签', help_text='到期是否续签')
    order_type = models.SmallIntegerField(choices=TYPE_LIST, default=1, verbose_name='签订类型', help_text='签订类型')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PURCHASE-合同管理'
        verbose_name_plural = verbose_name
        db_table = 'purchase_contract'

    def __str__(self):
        return self.name




