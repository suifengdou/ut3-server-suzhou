from django.db import models
from apps.bom.productline.models import ProductLine
from apps.bom.initialparts.models import InitialParts
from apps.auth.users.models import UserProfile
from apps.project.subunitproject.models import SubUnitProject
from apps.project.componentproject.models import ComponentProject
from apps.bom.initialparts.models import PartsCategory
from apps.bom.material.models import Material


class PhototypeProject(models.Model):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '开发预备'),
        (2, '开发阶段'),
        (3, '执行阶段'),
        (4, '评测阶段'),
        (5, '完成阶段'),
        (6, '开发中止')
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '子项项目必须标记才可确认'),
        (2, '产品线未查询到预制组件类型'),
        (3, '请检查错误，修复问题后，选择修复单据'),
        (4, '理赔必须设置需理赔才可以审核'),
        (5, '驳回原因为空'),
        (6, '无反馈内容, 不可以审核'),
    )
    TYPE_LIST = (
        (1, '主机'),
        (2, '附件'),
    )
    CATEGORY_LIST = (
        (1, '外观'),
        (2, '结构'),
        (3, '功能'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '确认开发'),
        (2, '确认更新'),
        (3, '确认组项'),
        (4, '手板'),
        (9, '驳回'),
    )
    name = models.CharField(unique=True, max_length=90, verbose_name='手板项目名', db_index=True, help_text='手板项目名')
    code = models.CharField(max_length=50, unique=True, verbose_name='手板项目编码', help_text='手板项目编码')
    category = models.SmallIntegerField(choices=CATEGORY_LIST, default=1, verbose_name='类型', help_text='类型')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, verbose_name='产品线', help_text='产品线')
    subunit_project = models.ForeignKey(SubUnitProject, on_delete=models.CASCADE, verbose_name='子项项目', help_text='子项项目')
    type = models.IntegerField(choices=TYPE_LIST, default=1, verbose_name='子项目类别', help_text='子项目类别')
    number = models.IntegerField(default=1, verbose_name='序号', help_text='序号')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='手板套数', help_text='手板套数')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态', help_text='工单状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-手板项目'
        verbose_name_plural = verbose_name
        unique_together = (("subunit_project", "number"), )
        db_table = 'project_phototype'

    def __str__(self):
        return str(self.id)


class PhototypeProjectDetails(models.Model):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '开发预备'),
        (2, '递交完成'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '未设置分组标识不可递交'),
        (2, '系统逻辑错误，请联系管理员处理'),
        (3, '同组标识手板执行单已经在开发，请驳回，再递交'),
        (4, '创建或归属执行单错误'),
        (5, '创建或更新执行单明细错误'),
        (6, '无反馈内容, 不可以审核'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '确认开发'),
        (2, '确认更新'),
        (3, '确认组项'),
        (4, '手板'),
        (9, '驳回'),
    )
    CATEGORY = (
        (1, '新项目'),
        (2, '改项目'),
        (3, '改单件'),
    )
    name = models.CharField(max_length=90, verbose_name='初始物料', help_text='初始物料')
    file_name =models.CharField(max_length=90, null=True, blank=True, verbose_name='文件名', help_text='文件名')
    code = models.CharField(max_length=90, verbose_name='初始物料编码', help_text='初始物料编码')
    phototype_project = models.ForeignKey(PhototypeProject, on_delete=models.CASCADE, verbose_name='手板项目名', help_text='手板项目名')
    initial_part = models.ForeignKey(InitialParts, on_delete=models.CASCADE, verbose_name='初始物料', help_text='初始物料')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, null=True, blank=True, verbose_name='产品线', help_text='产品线')
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
    quantity = models.IntegerField(null=True, blank=True, verbose_name='订量', help_text='订量')
    weight = models.IntegerField(null=True, blank=True, verbose_name='克重', help_text='克重')

    is_lacquered = models.BooleanField(default=False, verbose_name='是否喷漆', help_text='是否喷漆')
    is_group = models.BooleanField(default=False, verbose_name='是否组件', help_text='是否组件')
    color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='漆色号', help_text='漆色号')
    group_code = models.CharField(null=True, blank=True, max_length=60, verbose_name='分组标识', help_text='分组标识')

    is_making = models.BooleanField(default=False, verbose_name='是否制板', help_text='是否制板')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态', help_text='单据状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因', help_text='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签', help_text='处理标签')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'PROJECT-手板项目明细'
        verbose_name_plural = verbose_name
        db_table = 'project_phototype_details'

    def __str__(self):
        return self.name


class LogPhototypeProject(models.Model):

    obj = models.ForeignKey(PhototypeProject, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-手板项目-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_phototype_logging'

    def __str__(self):
        return str(self.id)


class LogPhototypeProjectDetails(models.Model):

    obj = models.ForeignKey(PhototypeProjectDetails, on_delete=models.CASCADE, verbose_name='对象', help_text='对象')
    name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    content = models.CharField(max_length=240, verbose_name='操作内容', help_text='操作内容')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = 'PROJECT-手板项目-日志'
        verbose_name_plural = verbose_name
        db_table = 'project_phototype_details_logging'

    def __str__(self):
        return str(self.id)


class PTFiles(models.Model):

    name = models.CharField(max_length=150, verbose_name='文件名称', help_text='文件名称')
    suffix = models.CharField(max_length=100, verbose_name='文件类型', help_text='文件类型')
    url = models.CharField(max_length=250, verbose_name='URL地址', help_text='URL地址')
    workorder = models.ForeignKey(PhototypeProject, on_delete=models.CASCADE, verbose_name='手板项目', help_text='手板项目')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'PROJECT-手板项目-文档'
        verbose_name_plural = verbose_name
        db_table = 'project_phototype_files'

    def __str__(self):
        return str(self.id)

