import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = Department
        fields = "__all__"

    def get_center(self, instance):
        try:
            ret = {
                "id": instance.center.id,
                "name": instance.center.name,
            }
        except:
            ret = {"id": -1, "name": "显示错误"}
        return ret


    def to_representation(self, instance):
        ret = super(DepartmentSerializer, self).to_representation(instance)
        ret["center"] = self.get_center(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        instance = self.Meta.model.objects.create(**validated_data)
        instance.d_id = str(instance.center.id + 100) + str(instance.id + 1000)[-3:]
        instance.save()
        return instance

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance