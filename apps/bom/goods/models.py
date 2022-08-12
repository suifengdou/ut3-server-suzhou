
from django.db import models
from apps.bom.middleparts.models import MiddlePartsVersion, MiddleParts
from apps.bom.initialparts.models import PartsCategory
from apps.auth.users.models import UserProfile


class AtomicParts(models.Model):

    name = models.CharField(max_length=50, unique=True, verbose_name='原子件', help_text='原子件')
    code = models.CharField(max_length=50, unique=True, verbose_name='原子件编码', help_text='原子件编码')
    middleparts = models.OneToOneField(MiddleParts, on_delete=models.CASCADE, verbose_name='中间件', help_text='中间件')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-原子件'
        verbose_name_plural = verbose_name
        db_table = 'bom_atomicparts'

    def __str__(self):
        return self.name


class AtomicPartsVersion(models.Model):

    name = models.CharField(max_length=60, unique=True, verbose_name='版本号名', help_text='版本号名')
    number = models.IntegerField(null=True, blank=True, verbose_name='版本', help_text='版本')
    code = models.IntegerField(null=True, blank=True, verbose_name='版本编码', help_text='版本编码')

    atomic_parts = models.ForeignKey(AtomicParts, on_delete=models.CASCADE, verbose_name='原子件', help_text='原子件')
    middlepartsversion = models.OneToOneField(MiddlePartsVersion, on_delete=models.CASCADE, verbose_name='中间件版本', help_text='中间件版本')

    is_lacquered = models.BooleanField(default=False, verbose_name='是否喷漆', help_text='是否喷漆')
    lacquer_color_number = models.CharField(null=True, blank=True, max_length=60, verbose_name='色号', help_text='色号')
    craft_content = models.CharField(null=True, blank=True, max_length=200, verbose_name='工艺内容', help_text='工艺内容')

    is_cell = models.BooleanField(default=False, verbose_name='是否单元', help_text='是否单元')
    cell_name = models.CharField(null=True, blank=True, max_length=90, verbose_name='单元名', help_text='单元名')
    cell_number = models.IntegerField(default=0, verbose_name='单元序号', help_text='单元序号')

    is_kit = models.BooleanField(default=False, verbose_name='是否套件', help_text='是否套件')
    kit_name = models.CharField(null=True, blank=True, max_length=90, verbose_name='套件名', help_text='套件名')
    kit_number = models.IntegerField(default=0, verbose_name='套件序号', help_text='套件序号')

    is_default = models.BooleanField(default=False, verbose_name='是否默认', help_text='是否默认')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'BOM-原子件版本'
        verbose_name_plural = verbose_name
        db_table = 'bom_atomicparts_version'

    def __str__(self):
        return self.name


class Goods(models.Model):

    CATEGORY_LIST = (
        (1, '原子'),
        (2, '单元'),
        (3, '套件'),
        (4, '整机'),
    )

    name = models.CharField(max_length=50, unique=True, verbose_name='货品', help_text='货品')
    code = models.CharField(max_length=50, unique=True, verbose_name='货品编码', help_text='货品编码')
    category = models.SmallIntegerField(choices=CATEGORY_LIST, default=1, verbose_name='货品类型', help_text='货品类型')
    is_atom = models.BooleanField(default=False, verbose_name='是否原子件', help_text='是否原子件')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-货品'
        verbose_name_plural = verbose_name
        db_table = 'bom_parts'

    def __str__(self):
        return self.name


class GoodsDetails(models.Model):

    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='货品', help_text='货品')
    atomic_parts = models.ForeignKey(AtomicParts, on_delete=models.CASCADE, verbose_name='原子件', help_text='原子件')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='用量', help_text='用量')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'BOM-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'bom_parts_details'

    def __str__(self):
        return self.goods.name

