import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import PLCategory, ProductLine
from apps.bom.productcore.models import ProductCore
from apps.bom.component.models import ComponentCategory


class PLCategorySerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = PLCategory
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

    def to_representation(self, instance):
        ret = super(PLCategorySerializer, self).to_representation(instance)
        ret['creator'] = self.get_creator(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


class ProductLineSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")
    component_details = serializers.JSONField(required=False)

    class Meta:
        model = ProductLine
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

    def get_component_details(self, instance):
        component_details = instance.productcore_set.all()
        ret = []
        for component_detail in component_details:
            data = {
                "id": component_detail.id,
                "component_category": {
                    "id": component_detail.component_category.id,
                    "name": component_detail.component_category.name
                },
                "memo": component_detail.memo
            }
            ret.append(data)
        return ret

    def check_component_details(self, component_details):
        for component in component_details:
            if not component.get("component_category", None):
                raise serializers.ValidationError("明细中组件类型为必填项！")
        component_list = list(map(lambda x: x["component_category"], component_details))
        component_check = set(component_list)
        if len(component_list) != len(component_check):
            raise serializers.ValidationError("明细中组件类型重复！")

    def create_component_detail(self, data):
        if data["id"] == 'n':
            data.pop("id", None)
            component_detail = ProductCore.objects.create(**data)
        else:
            pc_id = data.pop("id", None)
            component_detail = ProductCore.objects.filter(id=pc_id).update(**data)
        return component_detail

    def to_representation(self, instance):
        ret = super(ProductLineSerializer, self).to_representation(instance)
        ret['creator'] = self.get_creator(instance)
        ret['category'] = self.get_category(instance)
        ret["component_details"] = self.get_component_details(instance)
        return ret

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        component_details = validated_data.pop("component_details", [])
        self.check_component_details(component_details)

        product_line_order = self.Meta.model.objects.create(**validated_data)
        for component_detail in component_details:
            component_detail['product_line'] = product_line_order
            component_category = ComponentCategory.objects.filter(id=component_detail["component_category"])[0]
            component_detail["component_category"] = component_category
            component_detail.pop("xh")
            component_detail["creator"] = user
            self.create_component_detail(component_detail)
        return product_line_order

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_time"] = datetime.datetime.now()
        component_details = validated_data.pop("component_details", [])
        self.check_component_details(component_details)

        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        component_category_list = []
        for component_detail in component_details:
            component_detail['product_line'] = instance
            component_category_list.append(component_detail["component_category"])
            component_category = ComponentCategory.objects.filter(id=component_detail["component_category"])[0]
            component_detail["component_category"] = component_category
            component_detail.pop("xh")
            if component_detail["id"] == 'n':
                component_detail["creator"] = user
            self.create_component_detail(component_detail)
        component_category_now = ProductCore.objects.filter(product_line=instance)
        for check_detail in component_category_now:
            if check_detail.component_category.id not in component_category_list:
                check_detail.delete()
        return instance

