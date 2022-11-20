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
from .models import PhototypeExecuteProject, PhototypeExecuteProjectDetails, LogPhototypeExecuteProject, \
    LogPhototypeExecuteProjectDetails, PTEFiles
from apps.utils.logging.loggings import logging


class PhototypeExecuteProjectSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    initial_parts_details = serializers.JSONField(required=False)

    class Meta:
        model = PhototypeExecuteProject
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

    def get_subunit_project(self, instance):
        try:
            ret = {
                "id": instance.subunit_project.id,
                "subunit_name": instance.subunit_project.name,
                "subunit_code": instance.subunit_project.code,
                "unit_code": instance.subunit_project.unit_project.units_version.code,
            }
        except Exception as e:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_phototype_supplier(self, instance):
        try:
            ret = {
                "id": instance.phototype_supplier.id,
                "name": instance.phototype_supplier.name,
            }
        except Exception as e:
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

    def get_mistake_tag(self, instance):
        mistake_list = {
            0: '正常',
            1: '未确认物料不可审核',
            2: '已存在结算单，请联系管理员处理',
            3: '结算单创建错误',
            4: '结算单已审核不可驳回',
            5: '项目单状态不是准备状态不可驳回',
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
            ret = super(PhototypeExecuteProjectSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            ret['product_line'] = self.get_product_line(instance)
            ret['subunit_project'] = self.get_subunit_project(instance)
            ret['phototype_supplier'] = self.get_phototype_supplier(instance)
            ret['category'] = self.get_category(instance)
            ret['type'] = self.get_type(instance)
            ret['mistake_tag'] = self.get_mistake_tag(instance)
            ret['order_status'] = self.get_order_status(instance)
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
        logging(instance, user, LogPhototypeExecuteProject, "修改内容：%s" % str(content))
        return instance


class PhototypeExecuteProjectDetailsSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = PhototypeExecuteProjectDetails
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

    def get_subunit_project(self, instance):
        try:
            ret = {
                "id": instance.subunit_project.id,
                "name": instance.subunit_project.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_component_project(self, instance):
        try:
            ret = {
                "id": instance.component_project.id,
                "name": instance.component_project.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_phototype_execute_project(self, instance):
        try:
            ret = {
                "id": instance.phototype_execute_project.id,
                "name": instance.phototype_execute_project.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_category(self, instance):
        try:
            ret = {
                "id": instance.category.id,
                "name": instance.category.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_material(self, instance):
        try:
            ret = {
                "id": instance.material.id,
                "name": instance.material.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_mistake_tag(self, instance):
        mistake_list = {
            0: '正常',
            1: '未标记单据不可确认',
            2: '单价为零无特殊标记不可审核',
            3: '使用已有类型，必填物料编码',
            4: '无组项项目',
            5: '已存在物料，不可重复创建',
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

    def get_order_category(self, instance):
        order_category_list = {
            1: '全新创建',
            2: '使用已有',
        }
        try:
            ret = {
                "id": instance.order_category,
                "name": order_category_list.get(instance.order_category, None),
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def to_representation(self, instance):
            ret = super(PhototypeExecuteProjectDetailsSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            ret['product_line'] = self.get_product_line(instance)
            ret['subunit_project'] = self.get_subunit_project(instance)
            ret['component_project'] = self.get_component_project(instance)
            ret['phototype_execute_project'] = self.get_phototype_execute_project(instance)
            ret['category'] = self.get_category(instance)
            ret['material'] = self.get_material(instance)
            ret['order_category'] = self.get_order_category(instance)
            ret['mistake_tag'] = self.get_mistake_tag(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
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
        if "price" in validated_data:
            if validated_data["price"] > 0:
                validated_data["amount"] = validated_data["price"] * instance.quantity
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        logging(instance, user, LogPhototypeExecuteProjectDetails, "修改内容：%s" % str(content))
        return instance


class PTEFilesSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = PTEFiles
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
            ret = super(PTEFilesSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance





