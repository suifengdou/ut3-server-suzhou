
from django.db import models
from apps.bom.material.models import Material
from apps.bom.initialparts.models import PartsCategory
from apps.bom.productline.models import ProductLine
from apps.auth.users.models import UserProfile
from apps.bom.initialparts.models import InitialParts
from apps.project.unitproject.models import UnitProject
from apps.project.subunitproject.models import SubUnitProject
from apps.project.componentproject.models import ComponentProject


class OriInitialPartProject(models.Model):

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
        (1, '未确认物料不可审核'),
        (2, '全新创建类型不可填充物料编码'),
        (3, '使用已有类型，必填物料编码'),
        (4, '无组项项目'),
        (5, '已存在物料，不可重复创建'),
        (6, '创建初始物料出错'),
        (7, '物料编码错误'),
        (8, '单据类型错误'),
        (9, '创建初始物料项目出错'),
        (10, '物料类型错误'),
        (11, '组序号错误，联系管理员处理'),
        (12, '原初物料项目传递文档错误'),
        (13, '只有驳回订单才可以用处理驳回审核'),
    )

    PROCESSTAG = (
        (0, '未处理'),
        (1, '确认开发'),
        (9, '驳回'),
    )
    name = models.CharField(max_length=90, verbose_name='原初物料', help_text='初始物料')
    file_name =models.CharField(max_length=90, null=True, blank=True, verbose_name='文件名', help_text='文件名')
    code = models.CharField(max_length=90, null=True, blank=True, verbose_name='原初物料编码', help_text='初始物料编码')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, null=True, blank=True, verbose_name='产品线', help_text='产品线')
    unit_project = models.ForeignKey(UnitProject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='整机项目', help_text='整机项目')
    subunit_project = models.ForeignKey(SubUnitProject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='子项项目',
                              help_text='子项项目')
    component_project = models.ForeignKey(ComponentProject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='组项项目', help_text='组项项目')
    component_code = models.CharField(max_length=90, null=True, blank=True, verbose_name='组项编码', help_text='组项编码')
    category = models.ForeignKey(PartsCategory, on_delete=models.CASCADE, null=True, blank=True, verbose_name='类型', help_text='类型')
    diagram_number = models.IntegerField(null=True, blank=True, verbose_name='爆炸图号', help_text='爆炸图号')

    specification = models.CharField(null=True, blank=True, max_length=160, verbose_name='规格', help_text='规格')
    technology = models.CharField(null=True, blank=True, max_length=160, verbose_name='工艺', help_text='工艺')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, verbose_name='原材料', help_text='原材料')

    shrinkage = models.FloatField(null=True, blank=True, verbose_name='成型收缩率', help_text='成型收缩率')
    material_color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='材料色号',
                                             help_text='材料色号')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='用量', help_text='用量')
    weight = models.IntegerField(null=True, blank=True, verbose_name='克重', help_text='克重')

    is_lacquered = models.BooleanField(default=False, verbose_name='是否喷漆', help_text='是否喷漆')
    is_group = models.BooleanField(default=False, verbose_name='是否组件', help_text='是否组件')
    color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='色号', help_text='色号')
    group_code = models.IntegerField(null=True, blank=True, verbose_name='分组编码', help_text='分组编码')
    group_number = models.IntegerField(null=True, blank=True, verbose_name='分组序号', help_text='分组序号')

    is_making = models.BooleanField(default=False, verbose_name='是否制板', help_text='是否制板')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    initial_part = models.ForeignKey(InitialParts, on_delete=models.CASCADE, null=True, blank=True, verbose_name='初始物料', help_text='初始物料')
    order_category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='单据类型', help_text='单据类型')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态', help_text='单据状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-原始初始物料工作台'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_initial_part_project'
        unique_together = (("component_project", "name"),)

    def __str__(self):
        return self.name

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ["component_project", "order_category", "name", "file_name", "code", "category",
                        "diagram_number", "specification", "technology",  "material", "shrinkage",
                        "material_color_number", "weight", "quantity", "is_lacquered",
                        "color_number", "is_group", "group_number", "is_making", "memo"]

        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class InitialPartProject(models.Model):

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
    ori_order = models.OneToOneField(OriInitialPartProject, on_delete=models.CASCADE, verbose_name='源单', help_text='源单')
    name = models.CharField(max_length=90, verbose_name='初始物料', help_text='初始物料')
    file_name =models.CharField(max_length=90, null=True, blank=True, verbose_name='文件名', help_text='文件名')
    code = models.CharField(max_length=90, verbose_name='初始物料编码', help_text='初始物料编码')
    initial_part = models.ForeignKey(InitialParts, on_delete=models.CASCADE, verbose_name='初始物料', help_text='初始物料')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, null=True, blank=True, verbose_name='产品线', help_text='产品线')
    unit_project = models.ForeignKey(UnitProject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='整机项目', help_text='整机项目')
    subunit_project = models.ForeignKey(SubUnitProject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='子项项目',
                              help_text='子项项目')
    component_project = models.ForeignKey(ComponentProject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='组项目', help_text='组项目')
    component_code = models.CharField(max_length=90, null=True, blank=True, verbose_name='组项目编码', help_text='组项目编码')
    category = models.ForeignKey(PartsCategory, on_delete=models.CASCADE, null=True, blank=True, verbose_name='类型', help_text='类型')
    diagram_number = models.IntegerField(null=True, blank=True, verbose_name='爆炸图号', help_text='爆炸图号')

    specification = models.CharField(null=True, blank=True, max_length=160, verbose_name='规格', help_text='规格')
    technology = models.CharField(null=True, blank=True, max_length=160, verbose_name='工艺', help_text='工艺')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, verbose_name='原材料', help_text='原材料')

    shrinkage = models.FloatField(null=True, blank=True, verbose_name='成型收缩率', help_text='成型收缩率')
    material_color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='材料色号',
                                             help_text='材料色号')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='用量', help_text='用量')
    weight = models.IntegerField(null=True, blank=True, verbose_name='克重', help_text='克重')

    is_lacquered = models.BooleanField(default=False, verbose_name='是否喷漆', help_text='是否喷漆')
    is_group = models.BooleanField(default=False, verbose_name='是否组件', help_text='是否组件')
    color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='漆色号', help_text='漆色号')
    group_code = models.IntegerField(null=True, blank=True, verbose_name='分组编码', help_text='分组编码')
    group_number = models.IntegerField(null=True, blank=True, verbose_name='分组序号', help_text='分组序号')

    is_making = models.BooleanField(default=False, verbose_name='是否制板', help_text='是否制板')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='单据类型', help_text='单据类型')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态', help_text='单据状态')
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
        unique_together = (("component_project", "initial_part"),)

    def __str__(self):
        return self.name


class LogOriInitialPartProject(models.Model):
    obj = models.ForeignKey(OriInitialPartProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-原始初始物料工作台-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_initial_part_project_logging'

    def __str__(self):
        return self.name


class LogInitialPartProject(models.Model):
    obj = models.ForeignKey(InitialPartProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-初始物料工作台-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_initial_part_project_logging'

    def __str__(self):
        return self.name


class OIPPFiles(models.Model):
    name = models.CharField(max_length=150, verbose_name='文件名称', help_text='文件名称')
    suffix = models.CharField(max_length=100, verbose_name='文件类型', help_text='文件类型')
    url = models.CharField(max_length=250, verbose_name='URL地址', help_text='URL地址')
    workorder = models.ForeignKey(OriInitialPartProject, on_delete=models.CASCADE, verbose_name='原始初始物料项目', help_text='原始初始物料项目')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-原始初始物料项目-文档'
        verbose_name_plural = verbose_name
        db_table = 'project_ori_initial_part_project_files'

    def __str__(self):
        return str(self.id)


class IPPFiles(models.Model):
    name = models.CharField(max_length=150, verbose_name='文件名称', help_text='文件名称')
    suffix = models.CharField(max_length=100, verbose_name='文件类型', help_text='文件类型')
    url = models.CharField(max_length=250, verbose_name='URL地址', help_text='URL地址')
    workorder = models.ForeignKey(InitialPartProject, on_delete=models.CASCADE, verbose_name='初始物料项目', help_text='初始物料项目')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-初始物料项目-文档'
        verbose_name_plural = verbose_name
        db_table = 'project_initial_part_project_files'

    def __str__(self):
        return str(self.id)


