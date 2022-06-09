
from django.db import models
from apps.auth.users.models import UserProfile
from apps.bom.middleparts.models import MiddlePartsVersion
from apps.supplier.handboardsup.models import HandBoardSupplier


class HBExecution(models.Model):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '等待递交'),
        (2, '等待分配'),
        (3, '等待处理'),
        (4, '等待核算'),
        (5, '等待审核'),
        (6, '等待复核'),
        (7, '等待执行'),
        (8, '等待结算'),
        (9, '手板完结')
    )
    name = models.CharField(max_length=50, unique=True, verbose_name='手板制作单', help_text='手板制作单')
    units_id = models.CharField(max_length=50, unique=True, verbose_name='整机编码', help_text='整机编码')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'HB-手板'
        verbose_name_plural = verbose_name
        db_table = 'hb_handboard'

    def __str__(self):
        return self.name


class HBDetails(models.Model):

    handboard = models.ForeignKey(HandBoard, on_delete=models.CASCADE, verbose_name='手板', help_text='手板')
    name = models.CharField(max_length=50, unique=True, verbose_name='手板名称', help_text='手板名称')
    units_id = models.CharField(max_length=50, unique=True, verbose_name='整机编码', help_text='整机编码')
    middleparts = models.ForeignKey(MiddlePartsVersion, on_delete=models.CASCADE, verbose_name='中间件', help_text='中间件')
    is_lacquered = models.BooleanField(default=False, verbose_name='是否喷漆', help_text='是否喷漆')
    is_group = models.BooleanField(default=False, verbose_name='是否组件', help_text='是否组件')
    color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='色号', help_text='色号')
    group_number = models.IntegerField(null=True, blank=True, verbose_name='分组序号', help_text='分组序号')
    handboardsupplier = models.ForeignKey(HandBoardSupplier, on_delete=models.CASCADE, verbose_name='手板供应商', help_text='手板供应商')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'HB-手板'
        verbose_name_plural = verbose_name
        db_table = 'hb_handboard'

    def __str__(self):
        return self.name


class LogHandBoard(models.Model):
    handboard = models.ForeignKey(HandBoard, on_delete=models.CASCADE, verbose_name='手板', help_text='手板')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'HB-手板日志'
        verbose_name_plural = verbose_name
        db_table = 'hb_handboard_logging'

    def __str__(self):
        return self.name

