
from django.db import models
from apps.auth.users.models import UserProfile
from apps.bom.parts.models import AtomicPartsVersion
from apps.bom.units.models import Units
from apps.bom.component.models import ComponentVersion



class UnitUpdate(models.Model):

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
        (1, '原子件'),
        (2, '中间件'),
        (3, '模具'),
        (4, '组件'),
        (5, '子项'),
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
    unit = models.ForeignKey(Units, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')
    is_unique = models.BooleanField(default=False, verbose_name='是否限定', help_text='是否限定')
    category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='变更类型', help_text='变更类型')

    component = models.ForeignKey(ComponentVersion, on_delete=models.CASCADE, verbose_name='组件', help_text='组件')
    cause = models.CharField(null=True, blank=True, max_length=160, verbose_name='原因', help_text='原因')
    content = models.CharField(null=True, blank=True, max_length=160, verbose_name='内容', help_text='内容')
    amount = models.FloatField(default=0, verbose_name='总金额', help_text='总金额')
    period = models.IntegerField(default=0, verbose_name='变更天数', help_text='变更天数')
    laying_off = models.IntegerField(default=0, verbose_name='停工天数', help_text='停工天数')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'UPDATE-产品变更单'
        verbose_name_plural = verbose_name
        db_table = 'update_unitupdate'

    def __str__(self):
        return self.name


class UnitUpdateDetails(models.Model):
    BEFORE_CATEGORY = (
        (1, '正常使用'),
        (2, '用完更新'),
        (3, '额外加工'),
        (4, '完整报废'),
    )
    BEHIND_CATEGORY = (
        (1, '完全替换'),
        (2, '共存使用'),
        (3, '备用'),
    )
    atomic_parts = models.ForeignKey(AtomicPartsVersion, on_delete=models.CASCADE, verbose_name='原子件', help_text='原子件')
    before_category = models.SmallIntegerField(choices=BEFORE_CATEGORY, default=0, verbose_name='旧料处置', help_text='旧料处置')
    behind_category = models.SmallIntegerField(choices=BEHIND_CATEGORY, default=0, verbose_name='新料处置', help_text='新料处置')
    start_po = models.CharField(null=True, blank=True, max_length=160, verbose_name='起始单号', help_text='起始单号')
    plan = models.CharField(null=True, blank=True, max_length=160, verbose_name='变更方案', help_text='变更方案')
    scrap_quantity = models.IntegerField(default=0, verbose_name='报废数量', help_text='报废数量')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'UPDATE-产品变更单明细'
        verbose_name_plural = verbose_name
        db_table = 'update_unitupdate_details'

    def __str__(self):
        return self.atomic_parts__name


class LogUnitUpdate(models.Model):
    object = models.ForeignKey(UnitUpdate, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'UPDATE-产品变更单-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_units_logging'

    def __str__(self):
        return self.name


