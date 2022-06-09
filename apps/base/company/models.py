from django.db import models
import django.utils.timezone as timezone
import pandas as pd


class Company(models.Model):
    ORDER_STATUS = (
        (0, '未合作'),
        (1, '合作中'),
        (1, '解除合作'),
    )

    name = models.CharField(unique=True, max_length=30, verbose_name='公司简称', db_index=True, help_text='公司简称')
    full_name = models.CharField(null=True, blank=True, max_length=60, verbose_name='公司全称', help_text='公司全称')
    tax_fil_number = models.CharField(unique=True, null=True, blank=True, max_length=30, verbose_name='税号', help_text='税号')
    registered_capital = models.IntegerField(null=True, blank=True, verbose_name='注册资本', help_text='注册资本')
    paid_capital = models.IntegerField(null=True, blank=True, verbose_name='实缴资本', help_text='实缴资本')
    telephone = models.CharField(null=True, blank=True, max_length=60, verbose_name='电话', help_text='电话')
    accounts_bank = models.CharField(null=True, blank=True, max_length=100, verbose_name='开户行', help_text='开户行')
    account = models.CharField(null=True, blank=True, max_length=100, verbose_name='开户行账号', help_text='开户行账号')
    registered_address = models.CharField(null=True, blank=True, max_length=160, verbose_name='注册地址', help_text='注册地址')
    memo = models.CharField(null=True, blank=True, max_length=160, verbose_name='备注', help_text='备注')
    order_status = models.IntegerField(choices=ORDER_STATUS, default=1, verbose_name='状态', help_text='状态')
    created_time = models.DateTimeField(null=True, blank=True, verbose_name='公司创建时间', help_text='公司创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BASE-公司-公司管理'
        verbose_name_plural = verbose_name
        db_table = 'base_company'

    def __str__(self):
        return self.name




class Contacts(models.Model):

    GENDER_LIST = (
        (1, '男'),
        (2, '女'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='公司', help_text='公司')
    name = models.CharField(unique=True, max_length=200, db_index=True, verbose_name='联系人', help_text='联系人')
    mobile = models.CharField(unique=True, max_length=60, db_index=True, verbose_name='电话', help_text='联系人')
    email = models.CharField(unique=True, max_length=100, db_index=True, verbose_name='邮箱', help_text='联系人')
    position = models.CharField(null=True, blank=True, max_length=90, verbose_name='职位', help_text='职位')
    gender = models.IntegerField(choices=GENDER_LIST, default=1, verbose_name='性别', help_text='性别')
    is_staff = models.BooleanField(default=True, verbose_name='在职状态', help_text='在职状态')
    memo = models.CharField(max_length=200, null=True, blank=True, verbose_name='备注', help_text='备注')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')
    creator = models.CharField(null=True, blank=True, max_length=150, verbose_name='创建者', help_text='创建者')

    class Meta:
        verbose_name = 'BASE-公司-联系人'
        verbose_name_plural = verbose_name
        db_table = 'base_company_contacts'

    def __str__(self):
        return self.name


