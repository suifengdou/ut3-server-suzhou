from django.db import models


class Center(models.Model):

    name = models.CharField(max_length=50, unique=True, verbose_name='业务中心', help_text='业务中心')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BASE-业务中心-中心'
        verbose_name_plural = verbose_name
        db_table = 'base_center'

    def __str__(self):
        return self.name


