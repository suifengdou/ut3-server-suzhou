import datetime, math
import re
import pandas as pd
from decimal import Decimal
import numpy as np

import jieba
import jieba.posseg as pseg
import jieba.analyse
from collections import defaultdict

from rest_framework import viewsets, mixins, response
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ut3forsuzhou.permissions import Permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from .models import OriInitialPartProject, InitialPartProject, OIPPFiles, IPPFiles, LogOriInitialPartProject, LogInitialPartProject, PartsCategory
from .serializers import OriInitialPartProjectSerializer, InitialPartProjectSerializer, OIPPFilesSerializer, IPPFilesSerializer
from .filters import OriInitialPartProjectFilter, InitialPartProjectFilter, OIPPFilesFilter, IPPFilesFilter
from apps.utils.geography.models import City, District
from apps.utils.logging.loggings import logging, getlogs, getfiles
from apps.bom.productline.models import ProductLine
from apps.project.unitproject.models import UnitProject
from apps.project.subunitproject.models import SubUnitProject
from apps.project.componentproject.models import ComponentProject
from apps.bom.material.models import Material
from apps.bom.initialparts.models import InitialParts
from apps.utils.oss.aliyunoss import AliyunOSS
from ut3forsuzhou.settings import EXPORT_TOPLIMIT
from django.db.models import Max, Min, Sum


class OriInitialPartProjectSubmitViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定货品明细
    list:
        返回货品明细
    update:
        更新货品明细
    destroy:
        删除货品明细
    create:
        创建货品明细
    partial_update:
        更新部分货品明细
    """
    serializer_class = OriInitialPartProjectSerializer
    filter_class = OriInitialPartProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return OriInitialPartProject.objects.none()
        queryset = OriInitialPartProject.objects.filter(order_status=1).order_by("-id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["department"] = user.department
        params["order_status"] = 1
        f = OriInitialPartProjectFilter(params)
        serializer = OriInitialPartProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        department = self.request.user.department
        params["department"] = department
        if all_select_tag:
            handle_list = OriInitialPartProjectFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = OriInitialPartProject.objects.filter(id__in=order_ids, order_status=1)
            else:
                handle_list = []
        return handle_list

    @action(methods=['patch'], detail=False)
    def check(self, request, *args, **kwargs):
        user = request.user
        params = request.data
        check_list = self.get_handle_list(params)
        n = len(check_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        express_list = {
            1: "顺丰",
            2: "申通",
            3: "韵达",
        }
        if n:
            for obj in check_list:
                if int(obj.process_tag) != 1:
                    data["error"].append("%s 未确认物料不可审核" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 1
                    obj.save()
                    continue
                if obj.order_category == 1 and obj.code:
                    data["error"].append("%s 全新创建类型不可填充物料编码，查询是否真实全新创建" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 2
                    obj.save()
                    continue
                if obj.order_category == 2 and not obj.code:
                    data["error"].append("%s 使用已有类型，必填物料编码" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 3
                    obj.save()
                    continue
                if not obj.component_project:
                     data["error"].append("%s 无组项项目" % str(obj.id))
                     n -= 1
                     obj.mistake_tag = 4
                     obj.save()
                     continue
                if not obj.category:
                     data["error"].append("%s 物料类型错误" % str(obj.id))
                     n -= 1
                     obj.mistake_tag = 10
                     obj.save()
                     continue
                if obj.order_category == 1:
                    _q_initial_part_code = InitialParts.objects.filter(code=obj.code)
                    if _q_initial_part_code.exists():
                        data["error"].append("%s 已存在物料，不可重复创建，请选择已有类型" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 5
                        obj.save()
                        continue
                    else:

                        initial_part_order = InitialParts()
                        unit_code = obj.unit_project.units_version.units.code
                        part_name = "%s %s" % (str(obj.name), str(unit_code))
                        _q_initial_part_name = InitialParts.objects.filter(name=part_name)
                        if _q_initial_part_name.exists():
                            if not obj.initial_part:
                                data["error"].append("%s 已存在物料，不可重复创建，请选择已有类型" % str(obj.id))
                                n -= 1
                                obj.mistake_tag = 5
                                obj.save()
                                continue
                        if obj.group_number > 1000:
                            data["error"].append("%s 组序号错误，联系管理员处理" % str(obj.id))
                            n -= 1
                            obj.mistake_tag = 11
                            obj.save()
                            continue
                        initial_part_order.name = part_name
                        serial_number = 1000 + int(obj.group_number)
                        initial_part_order.code = "%s-%s-%s" % (str(obj.component_code), str(obj.category.code), str(serial_number)[-3:])
                        obj.code = initial_part_order.code
                        bom_order_fields = ["code", "category", "diagram_number", "specification",
                                        "technology", "material", "shrinkage", "material_color_number",
                                        "weight", "is_lacquered", "color_number", "memo"]
                        for b_key_work in bom_order_fields:
                            setattr(initial_part_order, b_key_work, getattr(obj, b_key_work, None))
                        try:
                            initial_part_order.creator = user
                            initial_part_order.save()
                            logging(obj, user, LogOriInitialPartProject, "生成初始物料：%s" % str(initial_part_order.name))
                        except Exception as e:
                            data["error"].append("%s 创建初始物料出错: %s" % (str(obj.id), e))
                            n -= 1
                            obj.mistake_tag = 6
                            obj.save()
                            continue

                elif obj.order_category == 2:
                    _q_initial_part = InitialParts.objects.filter(code=obj.code)
                    if _q_initial_part.exists():
                        initial_part_order = _q_initial_part[0]
                    else:
                        data["error"].append("%s 物料编码错误" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 7
                        obj.save()
                        continue
                else:
                    data["error"].append("%s 单据类型错误" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 8
                    obj.save()
                    continue

                initial_part_project = InitialPartProject()
                initial_part_project.initial_part = initial_part_order
                initial_part_project.ori_order = obj
                initial_part_project.name = initial_part_order.name
                project_order_fields = ["file_name", "code", "diagram_number", "specification", "technology",
                                        "shrinkage", "material_color_number", "quantity", "weight", "is_lacquered",
                                        "is_group", "color_number", "group_code", "is_making", "memo",
                                        "product_line", "unit_project", "subunit_project", "component_project",
                                        "component_code", "category", "material", "group_number"]
                for p_key_word in project_order_fields:
                    setattr(initial_part_project, p_key_word, getattr(obj, p_key_word, None))
                initial_part_project.creator = user
                try:
                    initial_part_project.save()
                    logging(obj, user, LogOriInitialPartProject, "创建初始物料项目：%s" % str(initial_part_project.name))
                    logging(initial_part_project, user, LogInitialPartProject, "创建")
                except Exception as e:
                    data["error"].append("%s创建初始物料项目出错: %s" % (str(obj.id), e))
                    n -= 1
                    obj.mistake_tag = 9
                    obj.save()
                    continue

                all_files = obj.oippfiles_set.all().filter(is_delete=False)
                if all_files:
                    file_error = 0
                    for file in all_files:
                        ippfile_order = IPPFiles()
                        ippfile_order.name = file.name
                        ippfile_order.suffix = file.suffix
                        ippfile_order.url = file.url
                        ippfile_order.workorder = initial_part_project
                        ippfile_order.creator = user
                        try:
                            ippfile_order.save()
                            logging(obj, user, LogOriInitialPartProject, "传递文档%s 到初始物料项目" % str(ippfile_order.name))
                            logging(initial_part_project, user, LogInitialPartProject, "创建文档：%s" % str(ippfile_order.name))
                        except Exception as e:
                            file_error = 1
                            data["error"].append("%s 原初物料项目传递文档错误：%s" % (str(obj.id), str(e)))
                            n -= 1
                            obj.mistake_tag = 12
                            obj.save()
                            break
                    if file_error:
                        continue

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.save()
                logging(obj, user, LogOriInitialPartProject, "审核物料")
        else:
            raise serializers.ValidationError("没有可审核的单据！")
        data["successful"] = n
        data["false"] = len(check_list) - n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def handle_reject(self, request, *args, **kwargs):
        user = request.user
        params = request.data
        check_list = self.get_handle_list(params)
        n = len(check_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        express_list = {
            1: "顺丰",
            2: "申通",
            3: "韵达",
        }
        if n:
            for obj in check_list:
                if int(obj.process_tag) != 9:
                    data["error"].append("%s 只有驳回订单才可以用处理驳回审核" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 13
                    obj.save()
                    continue
                if not obj.component_project:
                     data["error"].append("%s 无组项项目" % str(obj.id))
                     n -= 1
                     obj.mistake_tag = 4
                     obj.save()
                     continue
                if not obj.category:
                     data["error"].append("%s 物料类型错误" % str(obj.id))
                     n -= 1
                     obj.mistake_tag = 10
                     obj.save()
                     continue
                if obj.order_category == 1:
                    initial_part_order = obj.initial_part
                    unit_code = obj.unit_project.units_version.units.code
                    part_name = "%s %s" % (str(obj.name), str(unit_code))
                    if obj.group_number > 1000:
                        data["error"].append("%s 组序号错误，联系管理员处理" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 11
                        obj.save()
                        continue
                    initial_part_order.name = part_name
                    serial_number = 1000 + int(obj.group_number)
                    initial_part_order.code = "%s-%s-%s" % (str(obj.component_code), str(obj.category.code), str(serial_number)[-3:])
                    obj.code = initial_part_order.code
                    bom_order_fields = ["code", "category", "diagram_number", "specification",
                                    "technology", "material", "shrinkage", "material_color_number",
                                    "weight", "is_lacquered", "color_number", "memo"]
                    for b_key_work in bom_order_fields:
                        setattr(initial_part_order, b_key_work, getattr(obj, b_key_work, None))
                    try:
                        initial_part_order.creator = user
                        initial_part_order.save()
                        logging(obj, user, LogOriInitialPartProject, "更新初始物料：%s" % str(initial_part_order.name))
                    except Exception as e:
                        data["error"].append("%s 更新初始物料出错: %s" % (str(obj.id), e))
                        n -= 1
                        obj.mistake_tag = 6
                        obj.save()
                        continue

                elif obj.order_category == 2:
                    _q_initial_part = InitialParts.objects.filter(code=obj.code)
                    if _q_initial_part.exists():
                        initial_part_order = _q_initial_part[0]
                    else:
                        data["error"].append("%s 物料编码错误" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 7
                        obj.save()
                        continue
                else:
                    data["error"].append("%s 单据类型错误" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 8
                    obj.save()
                    continue

                initial_part_project = obj.initialpartproject
                initial_part_project.order_status = 1
                initial_part_project.ori_order = obj
                initial_part_project.name = initial_part_order.name
                project_order_fields = ["file_name", "code", "diagram_number", "specification", "technology",
                                        "shrinkage", "material_color_number", "quantity", "weight", "is_lacquered",
                                        "is_group", "color_number", "group_code", "is_making", "memo",
                                        "product_line", "unit_project", "subunit_project", "component_project",
                                        "component_code", "category", "material", "group_number", "order_category"]
                for p_key_word in project_order_fields:
                    setattr(initial_part_project, p_key_word, getattr(obj, p_key_word, None))
                initial_part_project.creator = user
                try:
                    initial_part_project.save()
                    logging(obj, user, LogOriInitialPartProject, "更新初始物料项目：%s" % str(initial_part_project.name))
                    logging(initial_part_project, user, LogInitialPartProject, "驳回更新完成")
                except Exception as e:
                    data["error"].append("%s更新初始物料项目出错: %s" % (str(obj.id), e))
                    n -= 1
                    obj.mistake_tag = 9
                    obj.save()
                    continue

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.process_tag = 1
                obj.save()
                logging(obj, user, LogOriInitialPartProject, "处理驳回物料")
        else:
            raise serializers.ValidationError("没有可处理的单据！")
        data["successful"] = n
        data["false"] = len(check_list) - n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def reject(self, request, *args, **kwargs):
        user = request.user
        params = request.data
        reject_list = self.get_handle_list(params)
        n = len(reject_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            for obj in reject_list:
                obj.order_status = 0
                logging(obj.ori_order, user, LogOriInitialPartProject, "物料被取消")
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def set_number(self, request, *args, **kwargs):
        params = request.data
        set_list = self.get_handle_list(params)
        n = len(set_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            component_projects = set(list(map(lambda x: x.component_project, set_list)))
            for component_project in component_projects:
                all_ori_initial_parts = component_project.oriinitialpartproject_set.all().filter(order_category=1)
                current_number = all_ori_initial_parts.aggregate(Max("group_number"))["group_number__max"]
                if not current_number:
                    current_number = 0
                handle_list = set_list.filter(component_project=component_project, order_category=1)
                for obj in handle_list:
                    if obj.group_number:
                        continue
                    current_number += 1
                    obj.group_number = current_number
                    obj.save()
            set_list.update(process_tag=1)
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def reset_tag(self, request, *args, **kwargs):
        params = request.data
        set_list = self.get_handle_list(params)
        n = len(set_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            set_list.update(process_tag=0)
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
            "组项版本编码": "component_project",
            "单据类型": "order_category",
            "物料名称": "name",
            "文件名": "file_name",
            "物料编码": "code",
            "类型": "category",
            "爆炸图号": "diagram_number",
            "规格": "specification",
            "工艺": "technology",
            "原材料": "material",
            "成型收缩率": "shrinkage",
            "材料色号": "material_color_number",
            "克重": "weight",
            "用量": "quantity",
            "是否喷漆": "is_lacquered",
            "漆色号": "color_number",
            "是否组件": "is_group",
            "分组序号": "group_code",
            "是否制板": "is_making",
            "备注": "memo"
        }

        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ["组项版本编码", "单据类型", "物料名称", "文件名", "物料编码", "类型", "爆炸图号", "规格",
                             "工艺", "原材料", "成型收缩率", "材料色号", "克重", "用量", "是否喷漆", "漆色号",
                             "是否组件", "分组序号", "是否制板", "备注"]

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
            _ret_verify_field = OriInitialPartProject.verify_mandatory(columns_key)
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
        user = request.user
        # 设置初始报告
        category_dic = {
            '全新创建': 1,
            '使用已有': 2,
        }
        judgment_dic = {
            "否": 0,
            "是": 1
        }

        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}
        for row in resource:
            judgment_fields = ["is_making",  "is_lacquered", "is_group"]
            for key_word in judgment_fields:
                row[key_word] = judgment_dic.get(row[key_word], None)
                if row[key_word] not in [1, 0]:
                    report_dic["error"].append("%s 是否喷漆, 是否组件, 是否制板只能填是或者否，不能为空。" % row["name"])
                    report_dic["false"] += 1
                    continue
            _q_component_project = ComponentProject.objects.filter(component_version__code=row["component_project"], order_status=2)
            if _q_component_project.exists():
                component_project = _q_component_project[0]
            else:
                report_dic["error"].append("%s 开发状态中无此组项项目" % row["component_project"])
                report_dic["false"] += 1
                continue
            _q_initial_prats_project = OriInitialPartProject.objects.filter(component_project=component_project, name=row["name"])
            if _q_initial_prats_project.exists():
                report_dic["error"].append("%s 同样货品名在同一组项版本中不可重复创建" % row["name"])
                report_dic["false"] += 1
                continue
            else:
                order = OriInitialPartProject()
                order.component_project = component_project
                order.product_line = component_project.product_line
                order.subunit_project = component_project.subunit_project
                order.unit_project = component_project.subunit_project.unit_project
                order.component_code = component_project.component_version.component.code
            _q_category = PartsCategory.objects.filter(name=row["category"])
            if _q_category.exists():
                order.category = _q_category[0]
            else:
                order.category = None
            order.order_category = category_dic.get(row["order_category"], None)

            _q_initial_prats = InitialParts.objects.filter(code=row["code"])
            if _q_initial_prats.exists():
                order_fields = ["name", "file_name", "code", "diagram_number", "quantity", "is_group", "group_code",
                                "is_making", "memo"]
                order.order_category = 2
            else:
                order.order_category = 1
                order_fields = ["name", "file_name", "code", "diagram_number", "specification",
                                "technology", "shrinkage", "material_color_number", "quantity", "weight",
                                "is_lacquered", "is_group", "color_number", "group_code", "is_making", "memo"]
                _q_material = Material.objects.filter(name=row["material"])
                if _q_material.exists():
                    order.material = _q_material[0]

            for key_word in order_fields:
                value = row.get(key_word, None)
                if str(value) == 'nan':
                    value = None
                setattr(order, key_word, value)

            order.creator = user
            try:
                order.save()
                report_dic["successful"] += 1
                logging(order, user, LogOriInitialPartProject, "创建")
            except Exception as e:
                report_dic["error"].append("%s 创建原初物料项目出错：%s" % (row["name"], str(e)))
                report_dic["false"] += 1

        return report_dic

    @action(methods=['patch'], detail=False)
    def photo_import(self, request, *args, **kwargs):
        user = request.user
        files = request.FILES.getlist("files", None)
        id = request.data.get('id', None)
        if id:
            work_order = OriInitialPartProject.objects.filter(id=id)[0]
        else:
            data = {
                "error": "系统错误联系管理员，无法回传单据ID！"
            }
            return Response(data)
        log_file_names = []
        if files:
            prefix = "ut3s2/project/origininitialparts"
            a_oss = AliyunOSS(prefix, files)
            file_urls = a_oss.upload()
            for obj in file_urls["urls"]:
                photo_order = OIPPFiles()
                photo_order.url = obj["url"]
                photo_order.name = obj["name"]
                log_file_names.append(obj["name"])
                photo_order.suffix = obj["suffix"]
                photo_order.workorder = work_order
                photo_order.creator = request.user
                photo_order.save()
            data = {
                "sucessful": "上传文件成功 %s 个" % len(file_urls["urls"]),
                "error": file_urls["error"]
            }
            logging(work_order, user, LogOriInitialPartProject, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class OriInitialPartProjectViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定货品明细
    list:
        返回货品明细
    update:
        更新货品明细
    destroy:
        删除货品明细
    create:
        创建货品明细
    partial_update:
        更新部分货品明细
    """
    serializer_class = OriInitialPartProjectSerializer
    filter_class = OriInitialPartProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return OriInitialPartProject.objects.none()
        queryset = OriInitialPartProject.objects.all().order_by("-id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        f = OriInitialPartProjectFilter(params)
        serializer = OriInitialPartProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = OriInitialPartProject.objects.filter(id=id)[0]
        ret = getlogs(instance, LogOriInitialPartProject)
        return Response(ret)

    @action(methods=['patch'], detail=False)
    def get_file_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = OriInitialPartProject.objects.filter(id=id)[0]
        ret = getfiles(instance, OIPPFiles)
        return Response(ret)


class InitialPartProjectConfirmViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定货品明细
    list:
        返回货品明细
    update:
        更新货品明细
    destroy:
        删除货品明细
    create:
        创建货品明细
    partial_update:
        更新部分货品明细
    """
    serializer_class = InitialPartProjectSerializer
    filter_class = InitialPartProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return InitialPartProject.objects.none()
        queryset = InitialPartProject.objects.filter(order_status=1).order_by("component_code")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["department"] = user.department
        params["order_status"] = 1
        f = InitialPartProjectFilter(params)
        serializer = InitialPartProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        department = self.request.user.department
        params["department"] = department
        if all_select_tag:
            handle_list = InitialPartProjectFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = InitialPartProject.objects.filter(id__in=order_ids, order_status=1)
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
        special_city = ['仙桃市', '天门市', '神农架林区', '潜江市', '济源市', '五家渠市', '图木舒克市', '铁门关市', '石河子市', '阿拉尔市',
                        '嘉峪关市', '五指山市', '文昌市', '万宁市', '屯昌县', '三亚市', '三沙市', '琼中黎族苗族自治县', '琼海市', '北屯市',
                        '陵水黎族自治县', '临高县', '乐东黎族自治县', '东方市', '定安县', '儋州市', '澄迈县', '昌江黎族自治县', '保亭黎族苗族自治县',
                        '白沙黎族自治县', '中山市', '东莞市']
        express_list = {
            1: "顺丰",
            2: "申通",
            3: "韵达",
        }
        if n:
            for obj in check_list:
                if not obj.erp_order_id:
                    _prefix = "MO"
                    serial_number = str(datetime.date.today()).replace("-", "")
                    obj.erp_order_id = serial_number + _prefix + str(obj.id)
                    obj.save()
                _q_mo_exp_repeat = ManualOrderExport.objects.filter(ori_order=obj)
                if _q_mo_exp_repeat.exists():
                    order = _q_mo_exp_repeat[0]
                    if order.order_status in [0, 1]:
                        order.order_status = 1
                        order.buyer_remark = ""
                        order.cs_memoranda = ""
                    else:
                        data["error"].append("%s重复递交" % obj.id)
                        n -= 1
                        obj.mistake_tag = 1
                        obj.save()
                        continue
                else:
                    order = ManualOrderExport()
                    order.erp_order_id = obj.erp_order_id
                if obj.order_category in [1, 2]:
                    if not all([obj.m_sn, obj.broken_part, obj.description]):
                        data["error"].append("%s售后配件需要补全sn、部件和描述" % obj.id)
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                if not obj.department:
                    data["error"].append("%s无部门" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 3
                    obj.save()
                    continue
                if not all([obj.province, obj.city]):
                    data["error"].append("%s省市不可为空" % obj.id)
                    n -= 1
                    obj.mistake_tag = 4
                    obj.save()
                    continue
                if obj.city.name not in special_city and not obj.district:
                    data["error"].append("%s 区县不可为空" % obj.id)
                    n -= 1
                    obj.mistake_tag = 4
                    obj.save()
                    continue
                if not re.match(r"^((0\d{2,3}-\d{7,8})|(1[3456789]\d{9}))$", obj.mobile):
                    data["error"].append("%s 手机错误" % obj.id)
                    n -= 1
                    obj.mistake_tag = 5
                    obj.save()
                    continue
                if not obj.shop:
                    data["error"].append("%s 无店铺" % obj.id)
                    n -= 1
                    obj.mistake_tag = 6
                    obj.save()
                    continue
                if '集运' in str(obj.address):
                    if obj.process_tag != 3:
                        data["error"].append("%s地址是集运仓" % obj.id)
                        n -= 1
                        obj.mistake_tag = 7
                        obj.save()
                        continue

                order.buyer_remark = "%s 的 %s 创建" % (str(obj.department), str(obj.creator))
                if obj.servicer:
                    order.buyer_remark = "%s来自%s" % (order.buyer_remark, str(obj.servicer))
                error_tag = 0
                export_goods_details = []
                all_goods_details = obj.mogoods_set.all()
                if len(all_goods_details) > 1:
                    order.cs_memoranda = "#"
                for goods_detail in all_goods_details:
                    _q_mo_repeat = MOGoods.objects.filter(manual_order__mobile=obj.mobile, goods_id=goods_detail.goods_id).order_by("-create_time")
                    if len(_q_mo_repeat) > 1:
                        if obj.process_tag != 3:
                            delta_date = (obj.create_time - _q_mo_repeat[1].create_time).days
                            if int(delta_date) < 14:
                                error_tag = 1
                                data["error"].append("%s 14天内重复" % obj.id)
                                n -= 1
                                obj.mistake_tag = 8
                                obj.save()
                                break
                            else:
                                error_tag = 1
                                data["error"].append("%s 14天外重复" % obj.id)
                                n -= 1
                                obj.mistake_tag = 9
                                obj.save()
                                break
                    if not export_goods_details:
                        export_goods_details = [goods_detail.goods_name.name, goods_detail.goods_id, goods_detail.quantity]
                    goods_info = "+ %sx%s" % (goods_detail.goods_name.name, goods_detail.quantity)
                    goods_id_info = "+ %s x%s" % (goods_detail.goods_id, goods_detail.quantity)
                    order.buyer_remark = str(order.buyer_remark) + goods_info
                    order.cs_memoranda = str(order.cs_memoranda) + goods_id_info
                if error_tag:
                    continue
                export_goods_fields = ["goods_name", "goods_id", "quantity"]
                for i in range(len(export_goods_details)):
                    setattr(order, export_goods_fields[i], export_goods_details[i])
                order_fields = ["shop", "nickname", "receiver", "address", "mobile", "province", "city", "district", "erp_order_id"]

                for field in order_fields:
                    setattr(order, field, getattr(obj, field, None))
                order.ori_order = obj
                if obj.assign_express:
                    express = express_list.get(obj.assign_express, None)
                    if express:
                        order.cs_memoranda = "%s 指定%s" % (order.cs_memoranda, express)
                try:
                    order.buyer_remark = "%s%s" % (order.buyer_remark, obj.memo)
                    order.creator = request.user.username
                    order.save()
                except Exception as e:
                    data["error"].append("%s输出单保存出错: %s" % (obj.id, e))
                    n -= 1
                    obj.mistake_tag = 10
                    obj.save()
                    continue

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.save()
        else:
            raise serializers.ValidationError("没有可审核的单据！")
        data["successful"] = n
        data["false"] = len(check_list) - n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def reject(self, request, *args, **kwargs):
        user = request.user
        params = request.data
        reject_list = self.get_handle_list(params)
        n = len(reject_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            for obj in reject_list:
                obj.ori_order.order_status = 1
                obj.ori_order.process_tag = 9
                obj.ori_order.save()
                obj.order_status = 0
                obj.save()
                logging(obj, user, LogInitialPartProject, "驳回物料到原初")
                logging(obj.ori_order, user, LogOriInitialPartProject, "物料被驳回")
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def set_special(self, request, *args, **kwargs):
        params = request.data
        set_list = self.get_handle_list(params)
        n = len(set_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            set_list.update(process_tag=3)
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def reset_tag(self, request, *args, **kwargs):
        params = request.data
        set_list = self.get_handle_list(params)
        n = len(set_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            set_list.update(process_tag=0)
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = InitialPartProject.objects.filter(id=id)[0]
        log_details = instance.loginitialpartproject_set.all().order_by("-id")
        ret = []
        for log_detail in log_details:
            data = {
                "id": log_detail.id,
                "name": log_detail.name.username,
                "content": log_detail.content,
                "created_time": log_detail.created_time
            }
            ret.append(data)
        return Response(ret)

    @action(methods=['patch'], detail=False)
    def photo_import(self, request, *args, **kwargs):
        user = request.user
        files = request.FILES.getlist("files", None)
        id = request.data.get('id', None)
        if id:
            work_order = InitialPartProject.objects.filter(id=id)[0]
        else:
            data = {
                "error": "系统错误联系管理员，无法回传单据ID！"
            }
            return Response(data)
        log_file_names = []
        if files:
            prefix = "ut3s2/project/initialparts"
            a_oss = AliyunOSS(prefix, files)
            file_urls = a_oss.upload()
            for obj in file_urls["urls"]:
                photo_order = IPPFiles()
                photo_order.url = obj["url"]
                photo_order.name = obj["name"]
                log_file_names.append(obj["name"])
                photo_order.suffix = obj["suffix"]
                photo_order.workorder = work_order
                photo_order.creator = request.user
                photo_order.save()
            data = {
                "sucessful": "上传文件成功 %s 个" % len(file_urls["urls"]),
                "error": file_urls["error"]
            }
            logging(work_order, user, LogInitialPartProject, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class InitialPartProjectViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定货品明细
    list:
        返回货品明细
    update:
        更新货品明细
    destroy:
        删除货品明细
    create:
        创建货品明细
    partial_update:
        更新部分货品明细
    """
    serializer_class = InitialPartProjectSerializer
    filter_class = InitialPartProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return InitialPartProject.objects.none()
        queryset = InitialPartProject.objects.all().order_by("-id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        f = InitialPartProjectFilter(params)
        serializer = InitialPartProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = InitialPartProject.objects.filter(id=id)[0]
        ret = getlogs(instance, LogInitialPartProject)
        return Response(ret)

    @action(methods=['patch'], detail=False)
    def get_file_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = InitialPartProject.objects.filter(id=id)[0]
        ret = getfiles(instance, IPPFiles)
        return Response(ret)


class OIPPFilesViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定货品明细
    list:
        返回货品明细
    update:
        更新货品明细
    destroy:
        删除货品明细
    create:
        创建货品明细
    partial_update:
        更新部分货品明细
    """
    serializer_class = OIPPFilesSerializer
    filter_class = OIPPFilesFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return OIPPFiles.objects.none()
        queryset = OIPPFiles.objects.all().order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def delete_file(self, request):
        id = request.data.get("id", None)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        user = request.user
        if id:
            photo_order = OIPPFiles.objects.filter(id=id, creator=user, is_delete=False)
            if photo_order.exists():
                photo_order = photo_order[0]
                photo_order.is_delete = 1
                photo_order.save()
                data["successful"] += 1
                logging(photo_order.workorder, user, LogOriInitialPartProject, "删除文档：%s" % photo_order.name)
            else:
                data["false"] += 1
                data["error"].append("只有创建者才有删除权限")
        else:
            data["false"] += 1
            data["error"].append("没有找到删除对象")
        return Response(data)


class IPPFilesViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定货品明细
    list:
        返回货品明细
    update:
        更新货品明细
    destroy:
        删除货品明细
    create:
        创建货品明细
    partial_update:
        更新部分货品明细
    """
    serializer_class = IPPFilesSerializer
    filter_class = IPPFilesFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return IPPFiles.objects.none()
        queryset = IPPFiles.objects.all().order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def delete_file(self, request):
        id = request.data.get("id", None)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        user = request.user
        if id:
            photo_order = IPPFiles.objects.filter(id=id, creator=user, is_delete=False)
            if photo_order.exists():
                photo_order = photo_order[0]
                photo_order.is_delete = 1
                photo_order.save()
                data["successful"] += 1
                logging(photo_order.workorder, user, LogInitialPartProject, "删除文档：%s" % photo_order.name)
            else:
                data["false"] += 1
                data["error"].append("只有创建者才有删除权限")
        else:
            data["false"] += 1
            data["error"].append("没有找到删除对象")
        return Response(data)

