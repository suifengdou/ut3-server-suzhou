import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Screw


class ScrewSerializer(serializers.ModelSerializer):
    material_list = {
        'CS': '碳钢',
        'SS': '不锈钢',
        'BR': '铜质',
    }
    head_type_list = {
        'B': '球面圆柱B头',
        'K': '平K头',
        'C': '圆柱C头',
        'F': '沉头',
        'H': '六角头',
        'HW': '六角头带垫圈',
        'O': '半沉O头',
        'P': '平元P头',
        'R': '半元R头',
        'PW': '平元头带垫圈',
        'T': '大扁T头',
        'V': '蘑菇头',
        'TW': '伞头',
    }
    tooth_type_list = {
        'A': '自攻尖尾疏A牙',
        'AB': '自攻尖尾密AB牙',
        'B': '自攻平尾疏B牙',
        'C': '自攻平尾密C牙',
        'P': '双牙丝P牙',
        'HL': '高低HL牙',
        'U': '玻璃牙纹U牙',
        'T': '自攻平尾切脚T牙',
        'AT': '自攻尖尾切脚AT牙',
        'M': '机械牙M牙',
        'BBT': 'B型三角牙',
        'CCT': 'C型三角牙',
        'PTT': 'P型三角牙',
        'STT': 'S型三角牙',
    }
    heat_treated_list = {
        "NT": "正火",
        "CA": "退火",
        "SHT": "固溶热",
        "SS": "固溶",
        "QT": "淬火",
        "B": "钎焊",
    }

    finish_list = {
        'DAC': '达克罗',
        'ZU': '蓝锌',
        'ZB': '黑锌',
        'ZC': '五彩锌',
        'ZI': '白锌',
        'BL': '氧化黑色',
        'GD': '氧化金色',
        'RU': '红铜',
        'YU': '黄铜',
        'CN': '镀铜底镍',
        'DT': '哑锡',
        'TP': '锡铅合金',
        'SA': '沙阳极',
        'NI': '亮镍',
        'EN': '无电解镍',
        'CR': '亮铬',
        'ET': '亮锡',
        'PS': '钝化',
        'AU': '镀金',
        'AG': '镀银',
        'TI': '镀钛',
        'ZF': '镀镉',
        'CH': '铬酸盐',
        'X': '素材',
        'EF': '电泳漆',
        'OT': '其他',
    }
    slot_list = {
        '+': '十字槽',
        '-': '一字槽',
        '△': '三角槽',
        '□': '内方槽',
        'T': '菊花槽',
        'HS': '内六角',
        'PZ': '米字槽',
        '+-': '十一槽',
        'Y': 'Y型槽',
        'H': '工字槽',
        'L': '止退花齿'
    }
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="创建时间", help_text="创建时间")
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label="更新时间", help_text="更新时间")

    class Meta:
        model = Screw
        fields = "__all__"

    def get_material(self, instance):
        try:
            ret = {
                "id": instance.material,
                "name": self.__class__.material_list.get(instance.material, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_heat_treated(self, instance):
        try:
            ret = {
                "id": instance.heat_treated,
                "name": self.__class__.heat_treated_list.get(instance.heat_treated, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_head_type(self, instance):
        try:
            ret = {
                "id": instance.head_type,
                "name": self.__class__.head_type_list.get(instance.head_type, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_tooth_type(self, instance):
        try:
            ret = {
                "id": instance.tooth_type,
                "name": self.__class__.tooth_type_list.get(instance.tooth_type, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_finish(self, instance):
        try:
            ret = {
                "id": instance.finish,
                "name": self.__class__.finish_list.get(instance.finish, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def get_slot_type(self, instance):
        try:
            ret = {
                "id": instance.slot_type,
                "name": self.__class__.slot_list.get(instance.slot_type, None)
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
                "name": instance.initial_parts.name,
            }
        except:
            ret = {"id": -1, "name": "无"}
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

    def get_order_status(self, instance):
        status_list = {
            0: "已取消",
            1: "待递交",
            2: "已完结",
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

    def get_mistake_tag(self, instance):
        mistake_list = {
            0: "正常",
            1: "同类型不可重复创建",
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

    def get_process_tag(self, instance):
        process_list = {
            0: "未分类",
        }
        try:
            ret = {
                "id": instance.process_tag,
                "name": process_list.get(instance.process_tag, None)
            }
        except:
            ret = {
                "id": -1,
                "name": "空"
            }
        return ret

    def to_representation(self, instance):
        ret = super(ScrewSerializer, self).to_representation(instance)
        ret["head_type"] = self.get_head_type(instance)
        ret["tooth_type"] = self.get_tooth_type(instance)
        ret["finish"] = self.get_finish(instance)
        ret["slot_type"] = self.get_slot_type(instance)
        ret["initial_parts"] = self.get_initial_parts(instance)
        ret["order_status"] = self.get_order_status(instance)
        ret["mistake_tag"] = self.get_mistake_tag(instance)
        ret["process_tag"] = self.get_process_tag(instance)
        ret["creator"] = self.get_creator(instance)
        ret["heat_treated"] = self.get_heat_treated(instance)
        ret["material"] = self.get_material(instance)
        return ret

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        try:
            diameter = int(validated_data['diameter'])
            length = int(validated_data['length'])
            if diameter == 0 or length == 0:
                raise ValidationError("牙径和长度不能为零")
        except Exception as e:
            raise ValidationError("牙径和长度错误")

        check_list = ['head_type', 'tooth_type', 'finish', 'slot_type']
        for index_word in check_list:
            check_content = validated_data[index_word]
            if not check_content:
                raise ValidationError("%s 必填项" % check_content)
        name_dic = ScrewSerializer.get_name_dic(validated_data)
        name = "%s%s%sX%s %s %s %s" % (name_dic["material"], name_dic["head_type"], str(validated_data["diameter"]), \
                                       str(validated_data["length"]), name_dic["tooth_type"], \
                                       name_dic["finish"], name_dic["slot_type"])
        screw_id = "M%sX%s%s-%s-%s-%s[%s]" % (str(validated_data["diameter"]), str(validated_data["length"]), \
                                              str(validated_data["material"]),  str(validated_data["head_type"]), \
                                              str(validated_data["tooth_type"]), str(validated_data["finish"]), \
                                              str(validated_data["slot_type"]))
        _q_check_id = Screw.objects.filter(screw_id=screw_id)
        if _q_check_id.exists():
            raise ValidationError("已经存在同类型的螺丝，编码：%s" % screw_id)
        validated_data["name"] = name
        validated_data["screw_id"] = screw_id
        return self.Meta.model.objects.create(**validated_data)

    @classmethod
    def get_name_dic(cls, validated_data):
        name_dic = {
            "material": cls.material_list.get(validated_data["material"], None),
            "head_type": cls.head_type_list.get(validated_data["head_type"], None),
            "tooth_type": cls.tooth_type_list.get(validated_data["tooth_type"], None),
            "finish": cls.finish_list.get(validated_data["finish"], None),
            "slot_type": cls.slot_list.get(validated_data["slot_type"], None)
        }
        return name_dic

    def update(self, instance, validated_data):
        name_dic = ScrewSerializer.get_name_dic(validated_data)
        name = "%s%s%sX%s %s %s %s" % (name_dic["material"], name_dic["head_type"], str(validated_data["diameter"]), \
                                       str(validated_data["length"]), name_dic["tooth_type"], \
                                       name_dic["finish"], name_dic["slot_type"])
        screw_id = "M%sX%s%s-%s-%s-%s[%s]" % (str(validated_data["diameter"]), str(validated_data["length"]), \
                                              str(validated_data["material"]),  str(validated_data["head_type"]), \
                                              str(validated_data["tooth_type"]), str(validated_data["finish"]), \
                                              str(validated_data["slot_type"]))
        _q_check_id = Screw.objects.filter(screw_id=screw_id)
        if _q_check_id.exists():
            raise ValidationError("已经存在同类型的螺丝，编码：%s" % screw_id)
        validated_data["name"] = name
        validated_data["screw_id"] = screw_id
        validated_data["updated_time"] = datetime.datetime.now()
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance

