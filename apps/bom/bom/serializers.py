import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import BOM, BOMDetails


class BOMSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = BOM
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

    def get_units(self, instance):
        try:
            ret = {
                "id": instance.units.id,
                "name": instance.units.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def to_representation(self, instance):
        ret = super(BOMSerializer, self).to_representation(instance)
        ret['creator'] = self.get_creator(instance)
        ret['units'] = self.get_units(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


class BOMDetailsSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = BOMDetails
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

    def get_version(self, instance):
        try:
            ret = {
                "id": instance.version.id,
                "name": instance.version.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_details(self, instance):
        try:
            ret = {
                "id": instance.details.id,
                "name": instance.details.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def to_representation(self, instance):
        ret = super(BOMDetailsSerializer, self).to_representation(instance)
        ret['creator'] = self.get_creator(instance)
        ret['version'] = self.get_version(instance)
        ret['details'] = self.get_details(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance



