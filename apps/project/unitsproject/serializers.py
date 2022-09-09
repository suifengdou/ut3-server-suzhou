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
from .models import OriginUnitProject, UnitProject, LogOriginUnitProject, OUPPhoto, UPPhoto
from apps.utils.logging.loggings import logging


class OriginUnitProjectSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    auto_set_number = serializers.JSONField(required=False)
    is_supplement = serializers.JSONField(required=False)
    is_set_suffix = serializers.JSONField(required=False)

    class Meta:
        model = OriginUnitProject
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

    def get_nationality(self, instance):
        try:
            ret = {
                "id": instance.nationality.id,
                "name": instance.nationality.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_level(self, instance):
        level_list = {
            0: '无',
            1: 'S',
            2: 'A',
            3: 'B',
            4: 'C',
        }
        try:
            ret = {
                "id": instance.level,
                "name": level_list.get(instance.level, None),
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

    def get_file_details(self, instance):
        file_details = instance.oupphoto_set.filter(is_delete=False)
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

    def get_log_details(self, instance):
        log_details = instance.logoriginunitproject_set.filter(obj=instance).order_by("-id")
        ret = []
        for log_detail in log_details:
            data = {
                "id": log_detail.id,
                "name": log_detail.name.username,
                "content": log_detail.content,
                "created_time": log_detail.created_time
            }
            ret.append(data)
        return ret

    def to_representation(self, instance):
        ret = super(OriginUnitProjectSerializer, self).to_representation(instance)
        ret['creator'] = self.get_creator(instance)
        ret['product_line'] = self.get_product_line(instance)
        ret['nationality'] = self.get_nationality(instance)
        ret['level'] = self.get_level(instance)
        ret['category'] = self.get_category(instance)
        ret["file_details"] = self.get_file_details(instance)
        ret["log_details"] = self.get_log_details(instance)
        ret["mistake_tag"] = self.get_mistake_tag(instance)
        return ret

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        if not all(['level' in validated_data, 'product_line' in validated_data, 'suffix' in validated_data, 'nationality' in validated_data]):
            raise ValidationError({"创建错误": "级别，产品线，后缀，国别必填"})
        nationality = validated_data["nationality"]
        if nationality.name == '中国':
            nationality_sign = None
        else:
            nationality_sign = str(nationality.abbreviation)
        max_unit_number_order = OriginUnitProject.objects.all().order_by("-unit_number").first()
        if max_unit_number_order:
            max_unit_number = max_unit_number_order.unit_number
        else:
            max_unit_number = 0
        max_serial_number_order = OriginUnitProject.objects.filter(product_line=validated_data['product_line']).order_by("-serial_number").first()
        if max_serial_number_order:
            max_serial_number = max_serial_number_order.serial_number
        else:
            max_serial_number = 0
        _q_suffix = OriginUnitProject.objects.filter(suffix=validated_data['suffix'], product_line=validated_data['product_line'], nationality=nationality)
        if _q_suffix.exists():
            raise ValidationError({"创建重复": "相同国别产品线下不可以创建相同后缀名"})
        auto_set_number = validated_data.pop("auto_set_number", False)
        is_supplement = validated_data.pop("is_supplement", False)
        if auto_set_number:
            validated_data['serial_number'] = max_serial_number + 1
            validated_data['unit_number'] = max_unit_number + 1
        else:
            if not all(['serial_number' in validated_data, 'unit_number' in validated_data]):
                raise ValidationError({"创建错误": "非自动填充时，整机排序,系列排序必填"})
            if int(validated_data['serial_number']) <= max_serial_number:
                raise ValidationError({"创建重复": "相同产品线下不可以创建相同系列排序"})
            _q_serial_number = OriginUnitProject.objects.filter(unit_number=validated_data['unit_number'])
            if _q_serial_number.exists():
                raise ValidationError({"创建重复": "整机排序不可重复"})
            else:
                if validated_data['unit_number'] < max_unit_number:
                    if not is_supplement:
                        raise ValidationError({"创建错误": "整机排序不可小于当前最大排序值"})
        product_line = validated_data['product_line']
        validated_data['is_named'] = product_line.is_named
        prefix_code = product_line.category.code
        check_num = str(validated_data['unit_number'])
        if nationality_sign:
            validated_data["name"] = "%s %s %s" % (str(product_line.name), str(validated_data['suffix']), nationality_sign)
        else:
            validated_data["name"] = "%s %s" % (str(product_line.name), str(validated_data['suffix']))

        validated_data["code"] = "%s%s" % (str(prefix_code), str(check_num))
        instance = self.Meta.model.objects.create(**validated_data)
        check_tag = logging(instance, user, LogOriginUnitProject, "创建")
        return instance

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        user = self.context["request"].user
        validated_data["creator"] = user
        nationality = validated_data["nationality"]
        if nationality.name == '中国':
            nationality_sign = None
        else:
            nationality_sign = str(nationality.abbreviation)
        if 'is_set_suffix' in validated_data:
            if validated_data['is_set_suffix']:
                _q_suffix = OriginUnitProject.objects.filter(suffix=validated_data['suffix'],
                                                             product_line=validated_data['product_line'],
                                                             nationality=nationality)
                if _q_suffix.exists():
                    raise ValidationError({"修改重复": "相同国别产品线下不可以创建相同后缀名"})
            else:
                validated_data["suffix"] = instance.suffix
        else:
            validated_data["suffix"] = instance.suffix
        product_line = validated_data['product_line']
        validated_data['is_named'] = product_line.is_named
        prefix_code = product_line.category.code
        check_num = str(validated_data['unit_number'])
        if nationality_sign:
            validated_data["name"] = "%s %s %s" % (str(product_line.name), str(validated_data['suffix']), nationality_sign)
        else:
            validated_data["name"] = "%s %s" % (str(product_line.name), str(validated_data['suffix']))

        validated_data["code"] = "%s%s" % (str(prefix_code), str(check_num))
        content = []
        for key, value in validated_data.items():
            if 'time' not in str(key):
                check_value = getattr(instance, key, None)
                if value != check_value:
                    content.append('%s 替换 %s' % (value, check_value))
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        check_tag = logging(instance, user, LogOriginUnitProject, "修改内容： %s" % str(content)[:200])
        return instance


class UnitProjectSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = UnitProject
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

    def get_ori_project(self, instance):
        try:
            ret = {
                "id": instance.ori_project.id,
                "name": instance.ori_project.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_name(self, instance):
        try:
            ret = {
                "id": instance.name.id,
                "name": instance.name.name,
                "code": instance.name.code,
                "serial_number": instance.name.units.serial_number,
                "unit_number": instance.name.units.unit_number,
                "is_name": instance.name.units.is_named,
                "nationality": instance.name.units.nationality.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
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

    def get_level(self, instance):
        level_list = {
            0: '无',
            1: 'S',
            2: 'A',
            3: 'B',
            4: 'C',
        }
        try:
            ret = {
                "id": instance.level,
                "name": level_list.get(instance.level, None),
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

    def get_file_details(self, instance):
        file_details = instance.upphoto_set.filter(is_delete=False)
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

    def get_log_details(self, instance):
        log_details = instance.logunitproject_set.filter(obj=instance).order_by("-id")
        ret = []
        for log_detail in log_details:
            data = {
                "id": log_detail.id,
                "name": log_detail.name.username,
                "content": log_detail.content,
                "created_time": log_detail.created_time
            }
            ret.append(data)
        return ret

    def to_representation(self, instance):
            ret = super(UnitProjectSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            ret['product_line'] = self.get_product_line(instance)
            ret['ori_project'] = self.get_ori_project(instance)
            ret['level'] = self.get_level(instance)
            ret['name'] = self.get_name(instance)
            ret['category'] = self.get_category(instance)
            ret['mistake_tag'] = self.get_mistake_tag(instance)
            ret['file_details'] = self.get_file_details(instance)
            ret['log_details'] = self.get_log_details(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


class OUPPhotoSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = OUPPhoto
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(OUPPhotoSerializer, self).to_representation(instance)
        return ret

    def to_internal_value(self, data):
        return super(OUPPhotoSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["update_time"] = datetime.datetime.now()
        create_time = validated_data.pop("create_time", "")
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


class UPPhotoSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = OUPPhoto
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(UPPhotoSerializer, self).to_representation(instance)
        return ret

    def to_internal_value(self, data):
        return super(UPPhotoSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["update_time"] = datetime.datetime.now()
        create_time = validated_data.pop("create_time", "")
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance

