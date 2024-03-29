import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import PhototypeSupplier


class PhototypeSupplierSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = PhototypeSupplier
        fields = "__all__"

    def get_level(self, instance):
        LEVEL_LIST = {
            0: "无",
            1: "S",
            2: "A",
            3: "B",
            4: "C",
        }
        try:
            ret = {
                "id": instance.level,
                "name": LEVEL_LIST.get(instance.level, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_order_status(self, instance):
        STATUS_LIST = {
            0: "未合作",
            1: "合作中",
            2: "解除合作",
        }
        try:
            ret = {
                "id": instance.order_status,
                "name": STATUS_LIST.get(instance.order_status, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

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

    def to_representation(self, instance):
        ret = super(PhototypeSupplierSerializer, self).to_representation(instance)
        ret["level"] = self.get_level(instance)
        ret["order_status"] = self.get_order_status(instance)
        ret["company"] = self.get_company(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance

