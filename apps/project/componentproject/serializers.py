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
from .models import ComponentProject
User = get_user_model()


class ComponentProjectSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ComponentProject
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

    def get_subunits_project(self, instance):
        try:
            ret = {
                "id": instance.subunits_project.id,
                "subunit_name": instance.subunits_project.subunits_version.name,
                "subunit_code": instance.subunits_project.subunits_version.code,
                "unit_code": instance.subunits_project.unit_project.name.code,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_component_version(self, instance):
        try:
            ret = {
                "id": instance.component_version.id,
                "name": instance.component_version.name,
                "code": instance.component_version.code,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret

    def get_component_category(self, instance):
        try:
            ret = {
                "id": instance.component_category.id,
                "name": instance.component_category.name,
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

    def to_representation(self, instance):
            ret = super(ComponentProjectSerializer, self).to_representation(instance)
            ret['creator'] = self.get_creator(instance)
            ret['product_line'] = self.get_product_line(instance)
            ret['subunits_project'] = self.get_subunits_project(instance)
            ret['component_version'] = self.get_component_version(instance)
            ret['component_category'] = self.get_component_category(instance)
            ret['category'] = self.get_category(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance




