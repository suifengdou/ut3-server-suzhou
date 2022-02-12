
from django.db import models

class Center(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='中心名称', help_text='中心名称')
    c_id = models.CharField(null=True, blank=True, max_length=50, verbose_name='中心ID', help_text='中心ID')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BASE-部门-中心管理'
        verbose_name_plural = verbose_name
        db_table = 'base_center'

    def __str__(self):
        return self.name


class Department(models.Model):

    name = models.CharField(max_length=50, unique=True, verbose_name='部门名称', help_text='部门名称')
    d_id = models.CharField(max_length=50, verbose_name='部门ID', help_text='部门ID')
    center = models.ForeignKey(Center, on_delete=models.CASCADE, null=True, blank=True, verbose_name='所属中心', help_text='所属中心')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BASE-部门-部门管理'
        verbose_name_plural = verbose_name
        db_table = 'base_department'

    def __str__(self):
        return self.name

