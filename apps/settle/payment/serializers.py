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
from .models import PaymentOrder, RelationPEPSToPay, PaymentOrderFiles, LogPaymentOrder, LogRelationPEPSToPay
from apps.utils.logging.loggings import logging


class PaymentOrderSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    component_details = serializers.JSONField(required=False)

    class Meta:
        model = PaymentOrder
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

    def get_supplier(self, instance):
        try:
            ret = {
                "id": instance.supplier.id,
                "name": instance.supplier.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_mistake_tag(self, instance):
        mistake_list = {
            0: '正常',
            1: '未标记单据不可确认',
            2: '手板付款单约束单错误，请联系管理员',
            3: '关联结算单状态必须是待审核，其他状态无法驳回',
            4: '整机版本错误联系管理员进行初始化',
            5: '整机版本创建错误',
            6: '整机项目创建错误',
        }
        try:
            ret = {
                "id": instance.mistake_tag,
                "name": mistake_list.get(instance.mistake_tag, None),
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_category(self, instance):
        category_list = {
            1: '手板付款单',
            2: '模具付款单',
            3: '订单付款单',
        }
        try:
            ret = {
                "id": instance.category,
                "name": category_list.get(instance.category, None),
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def to_representation(self, instance):
            ret = super(PaymentOrderSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            ret['supplier'] = self.get_supplier(instance)
            ret['mistake_tag'] = self.get_mistake_tag(instance)
            ret['category'] = self.get_category(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_time"] = datetime.datetime.now()

        # 改动内容
        content = []
        for key, value in validated_data.items():
            if 'time' not in str(key):
                check_value = getattr(instance, key, None)
                if value != check_value:
                    content.append('%s 替换 %s' % (value, check_value))

        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        logging(instance, user, LogPaymentOrder, "修改内容：%s" % str(content))
        return instance


class RelationPEPSToPaySerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = RelationPEPSToPay
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

    def get_origin_obj(self, instance):
        try:
            ret = {
                "id": instance.origin_obj.id,
                "name": instance.origin_obj.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_pay_obj(self, instance):
        try:
            ret = {
                "id": instance.pay_obj.id,
                "name": instance.pay_obj.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_order_status(self, instance):
        order_status_list = {
            0: '已取消',
            1: '待支付',
            2: '已支付',
        }
        try:
            ret = {
                "id": instance.order_status,
                "name": order_status_list.get(instance.order_status, None),
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_category(self, instance):
        category_list = {
            1: '正向约束',
            2: '逆向约束',
        }
        try:
            ret = {
                "id": instance.category,
                "name": category_list.get(instance.category, None),
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def to_representation(self, instance):
            ret = super(RelationPEPSToPaySerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            ret['order_status'] = self.get_order_status(instance)
            ret['category'] = self.get_category(instance)
            ret['origin_obj'] = self.get_origin_obj(instance)
            ret['pay_obj'] = self.get_pay_obj(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_time"] = datetime.datetime.now()
        # 改动内容
        content = []
        for key, value in validated_data.items():
            if 'time' not in str(key):
                check_value = getattr(instance, key, None)
                if value != check_value:
                    content.append('%s 替换 %s' % (value, check_value))

        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        logging(instance, user, LogRelationPEPSToPay, "修改内容：%s" % str(content))
        return instance


class PaymentOrderFilesSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = PaymentOrderFiles
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

    def to_representation(self, instance):
            ret = super(PaymentOrderFilesSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance




