from django.db import models
from apps.bom.productline.models import ProductLine
from apps.bom.component.models import ComponentCategory
from apps.auth.users.models import UserProfile


class ProductCore(models.Model):

    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, verbose_name='产品线', help_text='产品线')
    component_category = models.ForeignKey(ComponentCategory, on_delete=models.CASCADE, verbose_name='组件类型名', help_text='组件类型名')

    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='创建人', help_text='创建人')

    class Meta:
        verbose_name = 'BOM-产品线组件列表'
        verbose_name_plural = verbose_name
        db_table = 'bom_productcore'

    def __str__(self):
        return str(self.product_line.name)



