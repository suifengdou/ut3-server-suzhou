import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import AtomicParts, AtomicPartsVersion, Goods, GoodsDetails


class AtomicPartsSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = AtomicParts
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

    def get_middleparts(self, instance):
        try:
            ret = {
                "id": instance.middleparts.id,
                "name": instance.middleparts.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def to_representation(self, instance):
        ret = super(AtomicPartsSerializer, self).to_representation(instance)
        ret["creator"] = self.get_creator(instance)
        ret["middleparts"] = self.get_middleparts(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


class AtomicPartsVersionSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = AtomicPartsVersion
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

    def get_atomic_parts(self, instance):
        try:
            ret = {
                "id": instance.atomic_parts.id,
                "name": instance.atomic_parts.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_middlepartsversion(self, instance):
        try:
            ret = {
                "id": instance.middlepartsversion.id,
                "name": instance.middlepartsversion.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def to_representation(self, instance):
        ret = super(AtomicPartsVersionSerializer, self).to_representation(instance)
        ret["creator"] = self.get_creator(instance)
        ret["atomic_parts"] = self.get_atomic_parts(instance)
        ret["middlepartsversion"] = self.get_middlepartsversion(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


class GoodsSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = Goods
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

    def get_category(self, instance):
        category_list = {
            1: '原子',
            2: '单元',
            3: '套件',
        }
        try:
            ret = {
                "id": instance.category.id,
                "name": category_list.get(instance.category.id, None),
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def to_representation(self, instance):
        ret = super(GoodsSerializer, self).to_representation(instance)
        ret["creator"] = self.get_creator(instance)
        ret["category"] = self.get_category(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance


class GoodsDetailsSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = GoodsDetails
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

    def get_parts(self, instance):
        try:
            ret = {
                "id": instance.parts.id,
                "name": instance.parts.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def get_atomic_parts(self, instance):
        try:
            ret = {
                "id": instance.atomic_parts.id,
                "name": instance.atomic_parts.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
        return ret

    def to_representation(self, instance):
        ret = super(GoodsDetailsSerializer, self).to_representation(instance)
        ret["creator"] = self.get_creator(instance)
        ret["parts"] = self.get_parts(instance)
        ret["atomic_parts"] = self.get_atomic_parts(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.username
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance
