# -*- coding:utf-8 -*-

from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.base.company.models import Company
from apps.base.department.models import Department
from apps.auth.jobrole.models import JobRole


# Create your models here.
class UserProfile(AbstractUser):

    nick = models.CharField(null=True, blank=True, max_length=50, verbose_name='昵称', help_text='昵称')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, verbose_name='公司', help_text='公司')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, verbose_name='职属', help_text='职属')
    jobrole = models.ForeignKey(JobRole, on_delete=models.CASCADE, null=True, blank=True, verbose_name='职务', help_text='职务')
    is_our = models.BooleanField(default=False, verbose_name='是否本埠')

    class Meta:
        verbose_name = 'AUTH-用户信息'
        verbose_name_plural = verbose_name
        db_table = 'auth_userprofile'

    def __str__(self):
        return self.username


