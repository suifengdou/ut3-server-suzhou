from django.db import models
import django.utils.timezone as timezone
import pandas as pd


class JobRole(models.Model):
    ROLE_LEVEL = (
        (1, '职员'),
        (2, '主管'),
        (3, '经理'),
        (4, '总监'),
        (5, '总裁'),
    )

    name = models.CharField(unique=True, max_length=30, verbose_name='职务名称', db_index=True, help_text='职务名称')
    level = models.SmallIntegerField(choices=ROLE_LEVEL, default=1, verbose_name='职务层级', help_text='职务层级')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'AUTH-工作职务'
        verbose_name_plural = verbose_name
        db_table = 'auth_jobrole'

        permissions = (
            # (权限，权限描述),
            ('view_engineer_jobrole', 'Can view jobrole AUTH-工作职务-工程'),
            ('view_project_jobrole', 'Can view jobrole AUTH-工作职务-项目经理'),
            ('view_mould_jobrole', 'Can view jobrole AUTH-工作职务-模具'),
            ('view_devolopment_jobrole', 'Can view jobrole AUTH-工作职务-开发'),
            ('view_tester_jobrole', 'Can view jobrole AUTH-工作职务-实验'),
            ('view_purchase_jobrole', 'Can view jobrole AUTH-工作职务-采购'),
            ('view_quaility_jobrole', 'Can view jobrole AUTH-工作职务-质检'),
            ('view_order_jobrole', 'Can view jobrole AUTH-工作职务-订单'),
        )

    def __str__(self):
        return self.name


