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
from .models import HandBoard, LogHandBoard


class HandBoardSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = HandBoard
        fields = "__all__"

    def get_company(self, instance):
        try:
            ret = {
                "id": instance.company.id,
                "name": instance.company.name
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_order_status(self, instance):
        order_status = {
            0: "已被取消",
            1: "等待递交",
            2: "等待处理",
            3: "等待执行",
            4: "终审复核",
            5: "财务审核",
            6: "工单完结",
        }
        try:
            ret = {
                "id": instance.order_status,
                "name": order_status.get(instance.order_status, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_process_tag(self, instance):
        process_tag = {
            0: "未分类",
            1: "待截单",
            2: "签复核",
            3: "改地址",
            4: "催派查",
            5: "丢件核",
            6: "纠纷中",
            7: "需理赔",
            8: "其他类",
        }
        try:
            ret = {
                "id": instance.process_tag,
                "name": process_tag.get(instance.process_tag, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_mistake_tag(self, instance):
        mistake_list = {
            0: "正常",
            1: "快递单号错误",
            2: "处理意见为空",
            3: "返回的单据无返回单号",
            4: "丢件必须为需理赔才可以审核",
            5: "驳回原因为空",
            6: "无执行内容, 不可以审核",

        }
        try:
            ret = {
                "id": instance.mistake_tag,
                "name": mistake_list.get(instance.mistake_tag, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_category(self, instance):
        category = {
            1: "截单退回",
            2: "无人收货",
            3: "客户拒签",
            4: "修改地址",
            5: "催件派送",
            6: "虚假签收",
            7: "丢件破损",
            8: "其他异常",
        }
        try:
            ret = {
                "id": instance.category,
                "name": category.get(instance.category, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_handling_status(self, instance):
        handlings = {
            0: "未处理",
            1: "在处理",
            2: "待核实",
            3: "已处理",
        }
        try:
            ret = {
                "id": instance.handling_status,
                "name": handlings.get(instance.handling_status, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_photo_details(self, instance):
        photo_details = instance.ewophoto_set.all()
        ret = []
        for photo_detail in photo_details:
            data = {
                "id": photo_detail.id,
                "name": photo_detail.url,
            }
            ret.append(data)
        return ret

    def to_representation(self, instance):
        ret = super(HandBoardSerializer, self).to_representation(instance)
        ret["company"] = self.get_company(instance)
        ret["category"] = self.get_category(instance)
        ret["process_tag"] = self.get_process_tag(instance)
        ret["mistake_tag"] = self.get_mistake_tag(instance)
        ret["order_status"] = self.get_order_status(instance)
        ret["handling_status"] = self.get_handling_status(instance)
        ret["photo_details"] = self.get_photo_details(instance)
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



