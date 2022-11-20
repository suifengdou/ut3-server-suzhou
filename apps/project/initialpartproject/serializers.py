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
from .models import OriInitialPartProject, InitialPartProject, OIPPFiles, IPPFiles, PartsCategory, LogOriInitialPartProject, LogInitialPartProject
from apps.utils.logging.loggings import logging
User = get_user_model()


class OriInitialPartProjectSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = OriInitialPartProject
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
            1: '未确认物料不可审核',
            2: '全新创建类型不可填充物料编码',
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

    def get_file_details(self, instance):
        file_details = instance.oippfiles_set.filter(is_delete=False)
        ret = []
        for file_detail in file_details:
            if file_detail.suffix in ['png', 'jpg', 'gif', 'bmp', 'tif', 'svg', 'raw']:
                is_pic = True
            else:
                is_pic = False
            data = {
                "id": file_detail.id,
                "name": file_detail.name,
                "suffix": file_detail.suffix,
                "url": file_detail.url,
                "url_list": [file_detail.url],
                "is_pic": is_pic,
                "creator": file_detail.creator.username,
                "created_time": file_detail.created_time
            }
            ret.append(data)
        return ret

    def to_representation(self, instance):
        ret = super(OriInitialPartProjectSerializer, self).to_representation(instance)
        ret['creator'] = self.get_creator(instance)
        ret['product_line'] = self.get_product_line(instance)
        ret['unit_project'] = self.get_unit_project(instance)
        ret['subunit_project'] = self.get_subunit_project(instance)
        ret['component_project'] = self.get_component_project(instance)
        ret['category'] = self.get_category(instance)
        ret['material'] = self.get_material(instance)
        ret['order_category'] = self.get_order_category(instance)
        ret['file_details'] = self.get_file_details(instance)
        ret['mistake_tag'] = self.get_mistake_tag(instance)
        return ret

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        judgment_fields = ["is_making", "is_lacquered", "is_group"]
        for key_word in judgment_fields:
            if key_word not in validated_data:
                validated_data[key_word] = False
        component_project = validated_data["component_project"]
        _q_initial_prats_project = OriInitialPartProject.objects.filter(component_project=component_project,
                                                                        name=validated_data["name"])
        if _q_initial_prats_project.exists():
            raise ValidationError({"创建错误": "%s 同样货品名在同一组项版本中不可重复创建" % str(validated_data["name"])})
        else:
            validated_data["product_line"] = component_project.product_line
            validated_data["subunit_project"] = component_project.subunit_project
            validated_data["unit_project"] = component_project.subunit_project.unit_project
            validated_data["component_code"] = component_project.component_version.component.code
        instance = self.Meta.model.objects.create(**validated_data)
        logging(instance, user, LogOriInitialPartProject, "创建")
        return instance

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_time"] = datetime.datetime.now()
        component_project = validated_data["component_project"]
        if component_project != instance.component_project:
            validated_data["product_line"] = component_project.product_line
            validated_data["subunit_project"] = component_project.subunit_project
            validated_data["unit_project"] = component_project.subunit_project.unit_project
            validated_data["component_code"] = component_project.component_version.component.code
        # 改动内容
        content = []
        for key, value in validated_data.items():
            if 'time' not in str(key):
                check_value = getattr(instance, key, None)
                if value != check_value:
                    content.append('%s 替换 %s' % (value, check_value))

        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        logging(instance, user, LogOriInitialPartProject, "修改内容：%s" % str(content))
        return instance


class InitialPartProjectSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = InitialPartProject
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
            1: '未确认物料不可审核',
            2: '全新创建类型不可填充物料编码',
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

    def get_file_details(self, instance):
        file_details = instance.ippfiles_set.filter(is_delete=False)
        ret = []
        for file_detail in file_details:
            if file_detail.suffix in ['png', 'jpg', 'gif', 'bmp', 'tif', 'svg', 'raw']:
                is_pic = True
            else:
                is_pic = False
            data = {
                "id": file_detail.id,
                "name": file_detail.name,
                "suffix": file_detail.suffix,
                "url": file_detail.url,
                "url_list": [file_detail.url],
                "is_pic": is_pic,
                "creator": file_detail.creator.username,
                "created_time": file_detail.created_time
            }
            ret.append(data)
        return ret

    def to_representation(self, instance):
            ret = super(InitialPartProjectSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            ret['product_line'] = self.get_product_line(instance)
            ret['unit_project'] = self.get_unit_project(instance)
            ret['subunit_project'] = self.get_subunit_project(instance)
            ret['component_project'] = self.get_component_project(instance)
            ret['category'] = self.get_category(instance)
            ret['material'] = self.get_material(instance)
            ret['order_category'] = self.get_order_category(instance)
            ret['file_details'] = self.get_file_details(instance)
            ret['mistake_tag'] = self.get_mistake_tag(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_time"] = datetime.datetime.now()
        if "component_project" in validated_data:
            component_project = validated_data["component_project"]
            if component_project != instance.component_project:
                validated_data["product_line"] = component_project.product_line
                validated_data["subunit_project"] = component_project.subunit_project
                validated_data["unit_project"] = component_project.subunit_project.unit_project
                validated_data["component_code"] = component_project.component_version.component.code
            # 改动内容
        content = []
        for key, value in validated_data.items():
            if 'time' not in str(key):
                check_value = getattr(instance, key, None)
                if value != check_value:
                    content.append('%s 替换 %s' % (value, check_value))

        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        logging(instance, user, LogInitialPartProject, "修改内容：%s" % str(content))
        return instance


class OIPPFilesSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = OIPPFiles
        fields = "__all__"

    def to_representation(self, instance):
            ret = super(OIPPFilesSerializer, self).to_representation(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


class IPPFilesSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = IPPFiles
        fields = "__all__"

    def to_representation(self, instance):
            ret = super(IPPFilesSerializer, self).to_representation(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


