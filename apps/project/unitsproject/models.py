from django.db import models
import django.utils.timezone as timezone
import pandas as pd
from apps.auth.users.models import UserProfile
from apps.utils.geography.models import Nationality
from apps.bom.productline.models import ProductLine
from apps.bom.units.models import UnitsVersion, Units
from apps.bom.subunit.models import SubUnitVersion


class OriginUnitProject(models.Model):

    LEVEL_LIST = (
        (0, '无'),
        (1, 'S'),
        (2, 'A'),
        (3, 'B'),
        (4, 'C'),
    )
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '等待递交'),
        (2, '等待命名'),
        (3, '命名完成'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '产品线未定义组件类型'),
        (2, '请修复原始整机项目单'),
        (3, '生成整机出错'),
        (4, '整机版本错误联系管理员进行初始化'),
        (5, '整机版本创建错误'),
        (6, '整机项目创建错误'),

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
        (2, '版本迭代'),
    )

    name = models.CharField(unique=True, max_length=30, null=True, blank=True, verbose_name='整机项目名', db_index=True, help_text='整机项目名')
    code = models.CharField(unique=True, max_length=30, null=True, blank=True, verbose_name='整机项目编码', db_index=True, help_text='整机项目编码')
    suffix = models.CharField(max_length=50, null=True, blank=True, verbose_name='后缀', help_text='后缀')
    is_named = models.BooleanField(default=False, verbose_name='是否定名', help_text='是否定名')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, verbose_name='产品线', help_text='产品线')
    level = models.IntegerField(choices=LEVEL_LIST, default=0, verbose_name='级别', help_text='级别')
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, verbose_name='国别', help_text='国别')
    serial_number = models.IntegerField(default=0, null=True, blank=True, verbose_name='系列排序', help_text='系列排序')
    unit_number = models.IntegerField(unique=True, default=0, null=True, blank=True, verbose_name='整机排序', help_text='整机排序')
    category = models.SmallIntegerField(choices=CATEGORY_LIST, default=1, verbose_name='类型', help_text='类型')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    unit = models.OneToOneField(Units, on_delete=models.CASCADE, null=True, blank=True, verbose_name='整机', help_text='整机')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-原始整机项目工程'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_units'

    def __str__(self):
        return self.name


class UnitProject(models.Model):

    LEVEL_LIST = (
        (0, '无'),
        (1, 'S'),
        (2, 'A'),
        (3, 'B'),
        (4, 'C'),
    )
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '开发预备'),
        (2, '手板阶段'),
        (3, '试模阶段'),
        (4, '试产阶段'),
        (5, '量产阶段'),
        (6, '停产阶段'),
        (7, '开发中止')
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '标记单据错误，或者未标记'),
        (2, '保存子项失败'),
        (3, '保存子项版本失败'),
        (4, '创建子项项目失败'),
        (5, '驳回原因为空'),
        (6, '无反馈内容, 不可以审核'),
        (6, '标记单据错误，或者未标记'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '确认开发'),
        (2, '确认更新'),
    )
    CATEGORY_LIST = (
        (1, '开发构建'),
        (2, '版本迭代'),
    )
    category = models.SmallIntegerField(choices=CATEGORY_LIST, default=1, verbose_name='类型', help_text='类型')
    ori_project = models.OneToOneField(OriginUnitProject, on_delete=models.CASCADE, verbose_name='原始项目单', help_text='原始项目单')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, verbose_name='产品线', help_text='产品线')
    level = models.IntegerField(choices=LEVEL_LIST, default=0, verbose_name='级别', help_text='级别')
    name = models.OneToOneField(UnitsVersion, on_delete=models.CASCADE, verbose_name='整机版本', help_text='整机版本')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-整机项目工程'
        verbose_name_plural = verbose_name
        db_table = 'project_units'

    def __str__(self):
        return str(self.id)


class LogUnitProject(models.Model):

    obj = models.ForeignKey(UnitProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间', help_text='操作时间')

    class Meta:
        verbose_name = 'PROJECT-原始整机项目工程-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_units_logging'

    def __str__(self):
        return str(self.id)


class LogOriginUnitProject(models.Model):
    obj = models.ForeignKey(OriginUnitProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间', help_text='操作时间')

    class Meta:
        verbose_name = 'PROJECT-原始整机项目-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_units_logging'

    def __str__(self):
        return str(self.id)


class OUPPhoto(models.Model):
    name = models.CharField(max_length=150, verbose_name='文件名称', help_text='文件名称')
    suffix = models.CharField(max_length=100, verbose_name='文件类型', help_text='文件类型')
    url = models.CharField(max_length=250, verbose_name='URL地址', help_text='URL地址')
    workorder = models.ForeignKey(OriginUnitProject, on_delete=models.CASCADE, verbose_name='快递工单', help_text='快递工单')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-原始整机项目-图片'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_units_photo'

    def __str__(self):
        return str(self.id)


class UPPhoto(models.Model):
    name = models.CharField(max_length=150, verbose_name='文件名称', help_text='文件名称')
    suffix = models.CharField(max_length=100, verbose_name='文件类型', help_text='文件类型')
    url = models.CharField(max_length=250, verbose_name='URL地址', help_text='URL地址')
    workorder = models.ForeignKey(UnitProject, on_delete=models.CASCADE, verbose_name='整机项目', help_text='整机项目')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-整机项目-图片'
        verbose_name_plural = verbose_name
        db_table = 'project_units_photo'

    def __str__(self):
        return str(self.id)

