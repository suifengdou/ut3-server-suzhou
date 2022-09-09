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
from .models import HandBoard, HandBoardDetails


class HandBoardSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = HandBoard
        fields = "__all__"

    def get_creator(self, instance):
        try:
            ret = {
                "id": instance.creator.id,
                "name": instance.creator.username,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_subunit(self, instance):
        try:
            ret = {
                "id": instance.subunit.id,
                "name": instance.subunit.name
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_component(self, instance):
        try:
            ret = {
                "id": instance.component.id,
                "name": instance.component.name
            }
        except:
            ret = {
                "id": -1,
                "name": "无"
            }
        return ret

    def get_category(self, instance):
        category_list = {
            1: "外观",
            2: "结构",
            3: "功能",
        }
        try:
            ret = {
                "id": instance.category,
                "name": category_list.get(instance.category, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def to_representation(self, instance):
        ret = super(HandBoardSerializer, self).to_representation(instance)
        ret["creator"] = self.get_creator(instance)
        ret["category"] = self.get_category(instance)
        ret["subunit"] = self.get_subunit(instance)
        ret["component"] = self.get_component(instance)
        return ret

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        work_order = self.Meta.model.objects.create(**validated_data)

        return work_order

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        created_time = validated_data.pop("created_time", "")
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)

        return instance


class HandBoardDetailsSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = HandBoardDetails
        fields = "__all__"

    def get_handboard(self, instance):
        try:
            ret = {
                "id": instance.handboard.id,
                "name": instance.handboard.name
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_handboardsupplier(self, instance):
        try:
            ret = {
                "id": instance.handboardsupplier.id,
                "name": instance.handboardsupplier.name
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_initial_parts(self, instance):
        try:
            ret = {
                "id": instance.initial_parts.id,
                "name": instance.initial_parts.name
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def to_representation(self, instance):
        ret = super(HandBoardDetailsSerializer, self).to_representation(instance)
        ret["handboard"] = self.get_handboard(instance)
        ret["handboardsupplier"] = self.get_handboardsupplier(instance)
        ret["initial_parts"] = self.get_initial_parts(instance)
        return ret

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        work_order = self.Meta.model.objects.create(**validated_data)

        return work_order

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        created_time = validated_data.pop("created_time", "")
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)

        return instance

