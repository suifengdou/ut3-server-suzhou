import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import PartsCategory, InitialParts


class PartsCategorySerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = PartsCategory
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(PartsCategorySerializer, self).to_representation(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


class InitialPartsSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = InitialParts
        fields = "__all__"

    def get_category(self, instance):
        try:
            ret = {
                "id": instance.category.id,
                "name": instance.category.name
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_creator(self, instance):
        try:
            ret = {
                "id": instance.creator.id,
                "name": instance.creator.username,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_material(self, instance):
        try:
            ret = {
                "id": instance.material.id,
                "name": instance.material.username,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_order_status(self, instance):
        status_list = {
            0: "已取消",
            1: "待评审",
            2: "已评审",
        }
        try:
            ret = {
                "id": instance.order_status,
                "name": status_list.get(instance.order_status, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def to_representation(self, instance):
        ret = super(InitialPartsSerializer, self).to_representation(instance)
        ret['category'] = self.get_category(instance)
        ret['order_status'] = self.get_order_status(instance)
        ret['creator'] = self.get_creator(instance)
        ret['material'] = self.get_material(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance

