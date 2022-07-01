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
from .models import JobRole


class JobRoleSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = JobRole
        fields = "__all__"

    def get_level(self, instance):
        level_list = {
            1: "职员",
            2: "主管",
            3: "经理",
            4: "总监",
            5: "总裁"
        }
        try:
            ret = {
                "id": instance.level,
                "name": level_list.get(instance.level, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def to_representation(self, instance):
            ret = super(JobRoleSerializer, self).to_representation(instance)
            ret["level"] = self.get_level(instance)
            return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username

        user = JobRole.objects.create(**validated_data)
        return user

    def update(self, instance, validated_data):
        created_time = validated_data.pop("created_time", "")
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance

