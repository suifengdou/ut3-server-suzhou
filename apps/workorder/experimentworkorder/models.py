
from django.db import models
from apps.base.center.models import Center
from apps.auth.users.models import UserProfile
from apps.bom.units.models import Units, UnitsVersion


class ExperimentWorkorder(models.Model):
    STAGE_LIST = (
        (1, '手板'),
        (2, '试模'),
        (3, '试产'),
        (4, '量产'),
        (5, '其他'),
    )
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

    )
    PROCESSTAG = (
        (0, '未分类'),
        (1, '待截单'),

    )
    CATEGORY_LIST = (
        (1, '常规'),
        (2, '特约'),
    )

    name = models.CharField(max_length=50, unique=True, verbose_name='实验名称', help_text='实验名称')
    expriment_id = models.CharField(max_length=50, unique=True, verbose_name='实验编号', help_text='实验编号')
    units = models.ForeignKey(Units, on_delete=models.CASCADE, verbose_name='整机', help_text='整机')
    quantity = models.IntegerField(default=1, verbose_name='测试数量', help_text='测试数量')
    stage = models.SmallIntegerField(choices=STAGE_LIST, default=0, verbose_name='标的阶段', help_text='标的阶段')
    test_time = models.DateTimeField(null=True, blank=True, verbose_name='实验时间', help_text='实验时间')
    handler = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='handler', verbose_name='处理人',
                                help_text='处理人')

    result = models.BooleanField(default=False, verbose_name='实验结果', help_text='实验结果')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='更新时间', help_text='更新时间')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'WORKORDER-实验室工单'
        verbose_name_plural = verbose_name
        db_table = 'workorder_expriment'

    def __str__(self):
        return self.name


