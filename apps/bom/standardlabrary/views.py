
import pandas as pd
from rest_framework import viewsets, mixins, response
from rest_framework import status
from .serializers import ScrewSerializer
from .filters import ScrewFilter
from .models import Screw
from rest_framework.permissions import IsAuthenticated
from ut3forsuzhou.permissions import Permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from apps.bom.initialparts.models import InitialParts, PartsCategory


class ScrewSubmitViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定部门
    list:
        返回部门列表
    update:
        更新部门信息
    destroy:
        删除部门信息
    create:
        创建部门信息
    partial_update:
        更新部分部门字段
    """
    queryset = Screw.objects.all().order_by("id")
    serializer_class = ScrewSerializer
    filter_class = ScrewFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['material.view_material']
    }

    def get_queryset(self):
        if not self.request:
            return Screw.objects.none()
        department = self.request.user.department
        if not department:
            return Screw.objects.none()
        queryset = Screw.objects.filter(order_status=1).order_by("id")
        return queryset

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        if all_select_tag:
            handle_list = ScrewFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = Screw.objects.filter(id__in=order_ids, order_status=1)
            else:
                handle_list = []
        return handle_list

    @action(methods=['patch'], detail=False)
    def check(self, request, *args, **kwargs):
        params = request.data
        check_list = self.get_handle_list(params)
        n = len(check_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        heat_treated_list = {
            "NT": "正火",
            "CA": "退火",
            "SHT": "固溶热",
            "SS": "固溶",
            "QT": "淬火",
            "B": "钎焊",
        }
        if n:
            for obj in check_list:
                if obj.initial_parts:
                    data["error"].append("%s已经存在初始物料，不可重复递交" % obj.id)
                    n -= 1
                    obj.mistake_tag = 1
                    obj.save()
                    continue
                _q_initial_part = InitialParts.objects.filter(code=obj.code)
                if _q_initial_part.exists():
                    data["error"].append("%s已存在此编码物料，无法创建" % obj.id)
                    n -= 1
                    obj.mistake_tag = 2
                    obj.save()
                    continue
                order = InitialParts()
                _q_part_category = PartsCategory.objects.filter(name="螺丝")
                if _q_part_category.exists():
                    order.category = _q_part_category[0]
                else:
                    data["error"].append("%s配件种类缺螺丝" % obj.id)
                    n -= 1
                    obj.mistake_tag = 3
                    obj.save()
                    continue

                order.name = obj.name
                order.code = obj.code
                order.specification = obj.name.split(" ")[0]
                if obj.heat_treated:
                    order.technology ="%s %s" % (obj.name[len(order.specification):len(obj.name)], heat_treated_list.get(obj.heat_treated, None))
                else:
                    order.technology = obj.name[len(order.specification):len(obj.name)]
                order.weight = 20

                order.memo = obj.memo

                try:
                    order.creator = request.user
                    order.save()
                except Exception as e:
                    data["error"].append("%s创建初始物料出错: %s" % (obj.id, e))
                    n -= 1
                    obj.mistake_tag = 4
                    obj.save()
                    continue
                obj.initial_parts = order
                obj.order_status = 2
                obj.mistake_tag = 0
                obj.process_tag = 1
                obj.save()
        else:
            raise serializers.ValidationError("没有可审核的单据！")
        data["successful"] = n
        data["false"] = len(check_list) - n
        return Response(data)


    @action(methods=['patch'], detail=False)
    def fix(self, request, *args, **kwargs):
        params = request.data
        check_list = self.get_handle_list(params)
        n = len(check_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        heat_treated_list = {
            "NT": "正火",
            "CA": "退火",
            "SHT": "固溶热",
            "SS": "固溶",
            "QT": "淬火",
            "B": "钎焊",
        }
        if n:
            for obj in check_list:
                if obj.initial_parts:
                    obj.order_status = 2
                    obj.save()
                    continue
                _q_initial_part = InitialParts.objects.filter(code=obj.code)
                if _q_initial_part.exists():
                    obj.initial_parts = _q_initial_part[0]
                    obj.order_status = 2
                    obj.save()
                    continue
                else:
                    data["error"].append("%s非错误订单不要修复" % obj.id)
                    n -= 1
                    obj.mistake_tag = 5
                    obj.save()
                    continue
        else:
            raise serializers.ValidationError("没有可审核的单据！")
        data["successful"] = n
        data["false"] = len(check_list) - n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def reject(self, request, *args, **kwargs):
        params = request.data
        reject_list = self.get_handle_list(params)
        n = len(reject_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            reject_list.update(order_status=0)
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def excel_import(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            data = self.handle_upload_file(request, file)
        else:
            data = {
                "error": "上传文件未找到！"
            }

        return Response(data)

    def handle_upload_file(self, request, _file):
        ALLOWED_EXTENSIONS = ['xls', 'xlsx']
        INIT_FIELDS_DIC = {
            '材料名': 'name',
            '材质': 'texture',
            '硬度': 'hardness',
            '备注': 'memo',
        }

        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ["材料名", "材质", "硬度", "备注"]

            try:
                df = df[FILTER_FIELDS]
            except Exception as e:
                report_dic["error"].append("必要字段不全或者错误")
                return report_dic

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = Screw.verify_mandatory(columns_key)
            if _ret_verify_field is not None:
                return _ret_verify_field

            # 更改一下DataFrame的表名称
            columns_key_ori = df.columns.values.tolist()
            ret_columns_key = dict(zip(columns_key_ori, columns_key))
            df.rename(columns=ret_columns_key, inplace=True)

            # 更改一下DataFrame的表名称
            num_end = 0
            step = 300
            step_num = int(len(df) / step) + 2
            i = 1
            while i < step_num:
                num_start = num_end
                num_end = step * i
                intermediate_df = df.iloc[num_start: num_end]

                # 获取导入表格的字典，每一行一个字典。这个字典最后显示是个list
                _ret_list = intermediate_df.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(request, _ret_list)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
                i += 1
            return report_dic

        else:
            report_dic["error"].append('只支持excel文件格式！')
            return report_dic

    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        category_dic = {
            '质量问题': 1,
            '开箱即损': 2,
            '礼品赠品': 3
        }
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}
        for row in resource:
            order_fields = ["name", "texture", "hardness", "memo"]
            if not all([row["name"], row["texture"], row["hardness"]]):
                report_dic['error'].append("%s 数据不全" % row["name"])
                report_dic["false"] += 1
                continue
            order = Screw()
            for field in order_fields:
                setattr(order, field, row[field])
            try:
                order.creator = request.user.username
                order.save()
                report_dic["successful"] += 1
            except Exception as e:
                report_dic['error'].append("%s 保存出错" % row["name"])
                report_dic["false"] += 1

        return report_dic


class ScrewViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定部门
    list:
        返回部门列表
    update:
        更新部门信息
    destroy:
        删除部门信息
    create:
        创建部门信息
    partial_update:
        更新部分部门字段
    """
    queryset = Screw.objects.all().order_by("id")
    serializer_class = ScrewSerializer
    filter_class = ScrewFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['material.view_material']
    }

    @action(methods=['patch'], detail=False)
    def excel_import(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            data = self.handle_upload_file(request, file)
        else:
            data = {
                "error": "上传文件未找到！"
            }

        return Response(data)

    def handle_upload_file(self, request, _file):
        ALLOWED_EXTENSIONS = ['xls', 'xlsx']
        INIT_FIELDS_DIC = {
            '材料名': 'name',
            '材质': 'texture',
            '硬度': 'hardness',
            '备注': 'memo',
        }

        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ["材料名", "材质", "硬度", "备注"]

            try:
                df = df[FILTER_FIELDS]
            except Exception as e:
                report_dic["error"].append("必要字段不全或者错误")
                return report_dic

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = Screw.verify_mandatory(columns_key)
            if _ret_verify_field is not None:
                return _ret_verify_field

            # 更改一下DataFrame的表名称
            columns_key_ori = df.columns.values.tolist()
            ret_columns_key = dict(zip(columns_key_ori, columns_key))
            df.rename(columns=ret_columns_key, inplace=True)

            # 更改一下DataFrame的表名称
            num_end = 0
            step = 300
            step_num = int(len(df) / step) + 2
            i = 1
            while i < step_num:
                num_start = num_end
                num_end = step * i
                intermediate_df = df.iloc[num_start: num_end]

                # 获取导入表格的字典，每一行一个字典。这个字典最后显示是个list
                _ret_list = intermediate_df.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(request, _ret_list)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
                i += 1
            return report_dic

        else:
            report_dic["error"].append('只支持excel文件格式！')
            return report_dic

    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        category_dic = {
            '质量问题': 1,
            '开箱即损': 2,
            '礼品赠品': 3
        }
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}
        for row in resource:
            order_fields = ["name", "texture", "hardness", "memo"]
            if not all([row["name"], row["texture"], row["hardness"]]):
                report_dic['error'].append("%s 数据不全" % row["name"])
                report_dic["false"] += 1
                continue
            order = Screw()
            for field in order_fields:
                setattr(order, field, row[field])
            try:
                order.creator = request.user.username
                order.save()
                report_dic["successful"] += 1
            except Exception as e:
                report_dic['error'].append("%s 保存出错" % row["name"])
                report_dic["false"] += 1

        return report_dic

