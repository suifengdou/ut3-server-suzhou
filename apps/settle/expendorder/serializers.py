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
from .models import ExpendOrder, ExpendOrderDetails, LogExpendOrder, ExpendOrderFiles
from apps.utils.logging.loggings import logging


class ExpendOrderSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    component_details = serializers.JSONField(required=False)

    class Meta:
        model = ExpendOrder
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

    def get_product_line(self, instance):
        try:
            ret = {
                "id": instance.product_line.id,
                "name": instance.product_line.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_unit_project(self, instance):
        try:
            ret = {
                "id": instance.unit_project.id,
                "name": instance.unit_project.name,
                "nationality": instance.unit_project.units_version.units.nationality.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_subunits_version(self, instance):
        try:
            ret = {
                "id": instance.subunits_version.id,
                "name": instance.subunits_version.name,
                "code": instance.subunits_version.code,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_mistake_tag(self, instance):
        mistake_list = {
            0: '正常',
            1: '产品线未定义组件类型',
            2: '请修复原始整机项目单',
            3: '生成整机出错',
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

    def get_type(self, instance):
        type_list = {
            1: '主机',
            2: '附件',
        }
        try:
            ret = {
                "id": instance.type,
                "name": type_list.get(instance.type, None),
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_category(self, instance):
        category_list = {
            1: '开发构建',
            2: '版本迭代',
        }
        try:
            ret = {
                "id": instance.category,
                "name": category_list.get(instance.category, None),
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_component_details(self, instance):
        component_details = instance.componentproject_set.filter(subunit_project=instance, is_delete=False).order_by("-id")
        ret = []
        for component_detail in component_details:
            data = {
                "id": component_detail.id,
                "name": component_detail.component_version.name,
                "memo": component_detail.memo,
                "created_time": '{:%Y-%m-%d %H:%M:%S}'.format(component_detail.created_time)
            }
            ret.append(data)
        return ret

    def to_representation(self, instance):
            ret = super(ExpendOrderSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            ret['product_line'] = self.get_product_line(instance)
            ret['unit_project'] = self.get_unit_project(instance)
            ret['subunits_version'] = self.get_subunits_version(instance)
            ret['type'] = self.get_type(instance)
            ret['mistake_tag'] = self.get_mistake_tag(instance)
            ret['category'] = self.get_category(instance)
            ret['component_details'] = self.get_component_details(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_time"] = datetime.datetime.now()

        component_old = instance.componentproject_set.all()
        if component_old.filter(order_status__in=[2, 3, 4, 5, 6]):
            raise ValidationError({"更改错误": "组件已存在开发状态，不可更改"})
        component_new = validated_data["component_details"]
        component_new_list = []
        for obj in component_new:
            component_new_list.append(obj.id)
        for component_project in component_old:
            if component_project.id not in component_new_list:
                component_project.is_delete = True
                component_project.save()
                logging(instance, user, LogPaymentOrder, "删除了组项项目：%s" % component_project.component_version.name)
        return instance


class ExpendOrderDetailsSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ExpendOrderDetails
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

    def to_representation(self, instance):
            ret = super(ExpendOrderDetailsSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


class ExpendOrderFilesSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ExpendOrderFiles
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

    def to_representation(self, instance):
            ret = super(ExpendOrderFilesSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance




