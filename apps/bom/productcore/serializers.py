import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import ProductCore


class ProductCoreSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = ProductCore
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

    def get_product_line(self, instance):
        try:
            ret = {
                "id": instance.product_line.id,
                "name": instance.product_line.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_component_category(self, instance):
        try:
            ret = {
                "id": instance.component_category.id,
                "name": instance.component_category.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_order_status(self, instance):
        order_status_list = {
            0: '已取消',
            1: '待确认',
            2: '已完成',
        }
        try:
            ret = {
                "id": instance.order_status,
                "name": order_status_list.get(instance.order_status, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def to_representation(self, instance):
        ret = super(ProductCoreSerializer, self).to_representation(instance)
        ret['creator'] = self.get_creator(instance)
        ret['product_line'] = self.get_product_line(instance)
        ret['component_category'] = self.get_component_category(instance)
        ret['order_status'] = self.get_order_status(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance






