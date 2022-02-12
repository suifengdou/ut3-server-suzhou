from django.db import models

# Create your models here.

class GSeries(models.Model):
    name = models.CharField(unique=True, max_length=30, verbose_name='系列名称', db_index=True, help_text='系列名称')
    code = models.CharField(unique=True, max_length=30, verbose_name='系列编码', db_index=True, help_text='系列编码')
    memo = models.CharField(null=True, blank=True, max_length=230, verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BASE-货品-系列'
        verbose_name_plural = verbose_name
        db_table = 'base_goodscategory'

    def __str__(self):
        return self.name

class GUnit(models.Model):
    name = models.CharField(unique=True, max_length=30, verbose_name='单位名称', db_index=True, help_text='单位名称')
    code = models.CharField(unique=True, max_length=30, verbose_name='单位编码', db_index=True, help_text='单位编码')
    magnification = models.IntegerField(verbose_name='倍率', help_text='倍率')
    memo = models.CharField(null=True, blank=True, max_length=230, verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BASE-货品类别信息表'
        verbose_name_plural = verbose_name
        db_table = 'base_goodscategory'

    def __str__(self):
        return self.name

class GCategory(models.Model):
    name = models.CharField(unique=True, max_length=30, verbose_name='类型名称', db_index=True, help_text='类型名称')
    code = models.CharField(unique=True, max_length=30, verbose_name='类型编码', db_index=True, help_text='类型编码')

    memo = models.CharField(null=True, blank=True, max_length=230, verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BASE-货品-类型'
        verbose_name_plural = verbose_name
        db_table = 'base_goodscategory'

    def __str__(self):
        return self.name


class GMaterial(models.Model):
    name = models.CharField(unique=True, max_length=30, verbose_name='材料名称', db_index=True, help_text='材料名称')
    unit = models.ForeignKey(GCategory, on_delete=models.CASCADE, verbose_name='计价单位', help_text='计价单位')
    price = models.FloatField(default=0, verbose_name='单价', help_text='单价')

    memo = models.CharField(null=True, blank=True, max_length=230, verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BASE-货品-原材料'
        verbose_name_plural = verbose_name
        db_table = 'base_goodscategory'

    def __str__(self):
        return self.name



class PartsGoods(models.Model):

    goods_id = models.CharField(unique=True, max_length=30, verbose_name='货品编码', db_index=True, help_text='货品编码')
    series = models.ForeignKey(GSeries, on_delete=models.CASCADE, verbose_name='系列', help_text='系列')
    name = models.CharField(unique=True, max_length=60, verbose_name='货品名称', db_index=True, help_text='货品名称')
    category = models.ForeignKey(GCategory, on_delete=models.CASCADE, verbose_name='货品类别', help_text='货品类别')
    goods_number = models.CharField(unique=True, max_length=10, verbose_name='机器排序', help_text='机器排序')
    size = models.CharField(null=True, blank=True, max_length=50, verbose_name='规格', help_text='规格')
    width = models.IntegerField(null=True, blank=True, verbose_name='长', help_text='长')
    height = models.IntegerField(null=True, blank=True, verbose_name='宽', help_text='宽')
    depth = models.IntegerField(null=True, blank=True, verbose_name='高', help_text='高')
    price = models.FloatField(default=0, verbose_name='单价', help_text='单价')
    cost = models.FloatField(default=0, verbose_name='成本', help_text='成本')
    weight = models.IntegerField(null=True, blank=True, verbose_name='重量', help_text='重量')
    catalog_num = models.CharField(null=True, blank=True, max_length=230, verbose_name='爆炸图号', help_text='爆炸图号')
    memo = models.CharField(null=True, blank=True, max_length=230, verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BASE-货品信息'
        verbose_name_plural = verbose_name
        db_table = 'base_goodsinfo'
        permissions = (
            # (权限，权限描述),
            ('view_user_goods', 'Can view goods BASE-货品信息-查询'),
        )

    def __str__(self):
        return self.name

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ["goods_id", "name", "category", "goods_attribute", "goods_number", "size", "width",
                        "height", "depth", "weight", "catalog_num"]

        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None