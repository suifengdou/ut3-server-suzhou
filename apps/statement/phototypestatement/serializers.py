# -*- coding: utf-8 -*-
# @Time    : 2020/12/24 15:23
# @Author  : Hann
# @Site    : 
# @File    : serializers.py
# @Software: PyCharm

import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from rest_framework import status
from .models import PhototypeExecuteProjectStatement, LogPhototypeExecuteProjectStatement
from apps.utils.logging.loggings import logging


class PhototypeExecuteProjectStatementSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    initial_parts_details = serializers.JSONField(required=False)

    class Meta:
        model = PhototypeExecuteProjectStatement
        fields = "__all__"

    def get_creator(self, instance):
        try:
            ret = {
                "id": instance.creator.id,
                "name": instance.creator.username
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_project(self, instance):
        try:
            ret = {
                "id": instance.project.id,
                "name": instance.project.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_supplier(self, instance):
        try:
            ret = {
                "id": instance.supplier.id,
                "name": instance.supplier.name,
            }
        except Exception as e:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_order_status(self, instance):
        order_status_list = {
            0: '已被取消',
            1: '等待递交',
            2: '等待处理',
            3: '等待执行',
            4: '终审复核',
        }
        try:
            ret = {
                "id": instance.order_status,
                "name": order_status_list.get(instance.order_status, None),
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_mistake_tag(self, instance):
        mistake_list = {
            0: '正常',
            1: '未标记单据不可审核',
            2: '已拆分或者结算金额为零的订单不可用全额创建',
            3: '付款单关联关系错误，请联系管理员',
            4: '付款单创建失败',
            5: '付款关联关系单创建失败',
            6: '创建初始物料出错',
            7: '物料编码错误',
            8: '单据类型错误',
            9: '创建初始物料项目出错',
            10: '物料类型错误',
            11: '组序号错误，联系管理员处理',
            12: '原初物料项目传递文档错误',
            13: '只有驳回订单才可以用处理驳回审核',
        }
        try:
            ret = {
                "id": instance.mistake_tag,
                "name": mistake_list.get(instance.mistake_tag, None),
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def to_representation(self, instance):
            ret = super(PhototypeExecuteProjectStatementSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            ret['project'] = self.get_project(instance)
            ret['supplier'] = self.get_supplier(instance)
            ret['order_status'] = self.get_order_status(instance)
            ret['mistake_tag'] = self.get_mistake_tag(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_time"] = datetime.datetime.now()
        content = []
        for key, value in validated_data.items():
            if 'time' not in str(key):
                check_value = getattr(instance, key, None)
                if value != check_value:
                    content.append('%s 替换 %s' % (value, check_value))

        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        logging(instance, user, LogPhototypeExecuteProjectStatement, "修改内容：%s" % str(content))
        return instance


