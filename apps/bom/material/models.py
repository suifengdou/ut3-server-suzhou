
from django.db import models


class Material(models.Model):

    name = models.CharField(max_length=60, unique=True, verbose_name='材料名', help_text='材料名')
    texture = models.CharField(max_length=60, verbose_name='材质', help_text='材质')
    hardness = models.IntegerField(null=True, blank=True, verbose_name='硬度', help_text='硬度')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BOM-原材料'
        verbose_name_plural = verbose_name
        db_table = 'bom_material'

    def __str__(self):
        return self.name

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ["name", "texture", "hardness", "memo"]
        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None

