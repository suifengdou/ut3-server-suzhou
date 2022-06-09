
from django.db import models
from apps.bom.material.models import Material
from apps.bom.initialparts.models import PartsCategory
from apps.bom.productline.models import ProductLine
from apps.auth.users.models import UserProfile
from apps.bom.component.models import ComponentVersion
from apps.bom.units.models import UnitsVersion
from apps.bom.initialparts.models import InitialParts


class OriInitialPartsProject(models.Model):

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
        (1, '全新创建'),
        (2, '使用已有'),
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
    name = models.CharField(max_length=90, verbose_name='初始物料', help_text='初始物料')
    file_name =models.CharField(max_length=90, null=True, blank=True, verbose_name='文件名', help_text='文件名')
    mp_id = models.CharField(max_length=90, unique=True, null=True, blank=True, verbose_name='初始物料编码', help_text='初始物料编码')

    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, null=True, blank=True, verbose_name='产品线', help_text='产品线')
    units = models.ForeignKey(UnitsVersion, on_delete=models.CASCADE, null=True, blank=True, verbose_name='整机', help_text='整机')
    units_id = models.CharField(max_length=90, null=True, blank=True, verbose_name='整机编码', help_text='整机编码')
    component = models.ForeignKey(ComponentVersion, on_delete=models.CASCADE, null=True, blank=True, verbose_name='组', help_text='组')
    component_id = models.CharField(max_length=90, null=True, blank=True, verbose_name='组编码', help_text='组编码')
    category = models.ForeignKey(PartsCategory, on_delete=models.CASCADE, verbose_name='类型', help_text='类型')
    diagram_number = models.IntegerField(null=True, blank=True, verbose_name='爆炸图号', help_text='爆炸图号')

    specification = models.CharField(null=True, blank=True, max_length=160, verbose_name='规格', help_text='规格')
    technology = models.CharField(null=True, blank=True, max_length=160, verbose_name='工艺', help_text='工艺')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='原材料', help_text='原材料')

    Shrinkage = models.CharField(null=True, blank=True, verbose_name='成型收缩率', help_text='成型收缩率')
    material_color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='材料色号',
                                             help_text='材料色号')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='用量', help_text='用量')
    weight = models.IntegerField(null=True, blank=True, verbose_name='克重', help_text='克重')

    is_lacquered = models.BooleanField(default=False, verbose_name='是否喷漆', help_text='是否喷漆')
    is_group = models.BooleanField(default=False, verbose_name='是否组件', help_text='是否组件')
    color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='色号', help_text='色号')
    group_number = models.IntegerField(null=True, blank=True, verbose_name='分组序号', help_text='分组序号')

    is_handboard = models.BooleanField(default=False, verbose_name='是否制板', help_text='是否制板')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='工单类型', help_text='工单类型')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-原始初始物料工作台'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_initial_part_project'

    def __str__(self):
        return self.name


class InitialPartsProject(models.Model):

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
    name = models.CharField(max_length=90, verbose_name='初始物料', help_text='初始物料')
    file_name =models.CharField(max_length=90, null=True, blank=True, verbose_name='文件名', help_text='文件名')
    mp_id = models.CharField(max_length=90, unique=True, verbose_name='初始物料编码', help_text='初始物料编码')
    initial_part = models.ForeignKey(InitialParts, on_delete=models.CASCADE, verbose_name='初始物料', help_text='初始物料')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, null=True, blank=True, verbose_name='产品线', help_text='产品线')
    units = models.ForeignKey(Units, on_delete=models.CASCADE, null=True, blank=True, verbose_name='整机项目', help_text='整机项目')
    units_id = models.CharField(max_length=90, null=True, blank=True, verbose_name='整机项目编码', help_text='整机项目编码')
    component = models.ForeignKey(Component, on_delete=models.CASCADE, null=True, blank=True, verbose_name='组项目', help_text='组项目')
    component_id = models.CharField(max_length=90, null=True, blank=True, verbose_name='组项目编码', help_text='组项目编码')
    category = models.ForeignKey(PartsCategory, on_delete=models.CASCADE, verbose_name='类型', help_text='类型')
    diagram_number = models.IntegerField(null=True, blank=True, verbose_name='爆炸图号', help_text='爆炸图号')

    specification = models.CharField(null=True, blank=True, max_length=160, verbose_name='规格', help_text='规格')
    technology = models.CharField(null=True, blank=True, max_length=160, verbose_name='工艺', help_text='工艺')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='原材料', help_text='原材料')

    Shrinkage = models.CharField(null=True, blank=True, verbose_name='成型收缩率', help_text='成型收缩率')
    material_color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='材料色号',
                                             help_text='材料色号')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='用量', help_text='用量')
    weight = models.IntegerField(null=True, blank=True, verbose_name='克重', help_text='克重')

    is_lacquered = models.BooleanField(default=False, verbose_name='是否喷漆', help_text='是否喷漆')
    is_group = models.BooleanField(default=False, verbose_name='是否组件', help_text='是否组件')
    color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='色号', help_text='色号')
    group_number = models.IntegerField(null=True, blank=True, verbose_name='分组序号', help_text='分组序号')

    is_handboard = models.BooleanField(default=False, verbose_name='是否制板', help_text='是否制板')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='工单类型', help_text='工单类型')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-初始物料工作台'
        verbose_name_plural = verbose_name
        db_table = 'project_initial_part_project'

    def __str__(self):
        return self.name


class LogOriInitialPartsProject(models.Model):
    object = models.ForeignKey(OriInitialPartsProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-原始初始物料工作台-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_initial_part_project_logging'

    def __str__(self):
        return self.name


class LogInitialPartsProject(models.Model):
    object = models.ForeignKey(InitialPartsProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-初始物料工作台-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_initial_part_project_logging'

    def __str__(self):
        return self.name

