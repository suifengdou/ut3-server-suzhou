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
from .models import SubUnitProject, SUPFiles, LogSubUnitProject
from .serializers import SubUnitProjectSerializer, SUPFilesSerializer
from .filters import SubUnitProjectFilter, SUPFilesFilter
from apps.utils.oss.aliyunoss import AliyunOSS
from apps.utils.geography.tools import PickOutAdress
from ut3forsuzhou.settings import EXPORT_TOPLIMIT
from apps.utils.logging.loggings import logging
from apps.project.componentproject.models import ComponentProject, LogComponentProject
from apps.bom.component.models import Component, ComponentVersion
from apps.bom.productcore.models import ProductCore


class SubUnitProjectPrepareViewset(viewsets.ModelViewSet):
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
    serializer_class = SubUnitProjectSerializer
    filter_class = SubUnitProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return SubUnitProject.objects.none()
        queryset = SubUnitProject.objects.filter(order_status=1).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 1
        f = SubUnitProjectFilter(params)
        serializer = SubUnitProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        if all_select_tag:
            handle_list = SubUnitProjectFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = SubUnitProject.objects.filter(id__in=order_ids, order_status=1)
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
        if n:
            for obj in check_list:
                if obj.process_tag == 0:
                    data["error"].append("%s 子项项目必须标记才可确认" % obj.id)
                    n -= 1
                    obj.mistake_tag = 1
                    obj.save()
                    continue
                _q_component_project = obj.componentproject_set.all()
                if not _q_component_project.exists():
                    _q_productcore = ProductCore.objects.filter(product_line=obj.product_line, component_category__type=obj.type)
                    if _q_productcore.exists():
                        error_tag = 0
                        for c_category in _q_productcore:
                            component_order = Component()
                            component_order.category = c_category.component_category
                            preffix = re.sub("[\(（](.+?)[\)）]", "", str(c_category.component_category.name))
                            suffix_code = str(obj.unit_project.name.units.code)
                            preffix_code = str(obj.subunits_version.subunit.code)
                            component_order.name = "%s %s" % (preffix, suffix_code)
                            component_order.code = "%s-%s" % (preffix_code, str(c_category.component_category.code))
                            component_order.creator = user
                            try:
                                component_order.save()
                                logging(obj, user, LogSubUnitProject, "创建组项：%s" % component_order.name)
                            except Exception as e:
                                data["error"].append("%s 组项创建错误：%s" % (component_order.name, e))
                                error_tag = 1
                                continue
                            component_version = ComponentVersion()
                            suffix_version = "V001"
                            component_version.name = "%s %s" % (component_order.name, suffix_version)
                            component_version.code = "%s%s" % (component_order.code, suffix_version)
                            component_version.number = 1
                            component_version.component = component_order
                            component_version.creator = user
                            try:
                                component_version.save()
                                logging(obj, user, LogSubUnitProject, "创建组项版本：%s" % component_version.name)
                            except Exception as e:
                                data["error"].append("%s 组项版本创建错误： %s" % (component_version.name, e))
                                error_tag = 1
                                continue
                            component_project = ComponentProject()
                            component_project.category = obj.category
                            component_project.subunits_project = obj
                            component_project.product_line = obj.product_line
                            component_project.component_version = component_version
                            component_project.component_category = c_category.component_category
                            component_project.creator = user
                            try:
                                component_project.save()
                                logging(obj, user, LogSubUnitProject, "创建了组项项目：%s" % component_version.name)
                                logging(component_project, user, LogComponentProject, "创建")
                            except Exception as e:
                                data["error"].append("%s 组项项目创建错误： %s" % (component_version.name, e))
                                error_tag = 1
                                continue
                        if error_tag:
                            data["error"].append("%s 请检查错误，修复问题后，选择修复单据" % obj.id)
                            n -= 1
                            obj.mistake_tag = 3
                            obj.save()
                            continue
                    else:
                        data["error"].append("%s 产品线未查询到预制组件类型" % obj.id)
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.save()
                logging(obj, user, LogSubUnitProject, "确认项目单据")
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
            for obj in reject_list:
                obj.mogoods_set.all().delete()
            reject_list.update(order_status=0)
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def set_confirm(self, request, *args, **kwargs):
        params = request.data
        user = request.user
        set_list = self.get_handle_list(params)
        n = len(set_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            for obj in set_list:
                obj.process_tag = 1
                obj.save()
                logging(obj, user, LogSubUnitProject, "标记确认项目")
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def reset_tag(self, request, *args, **kwargs):
        params = request.data
        user = request.user
        set_list = self.get_handle_list(params)
        n = len(set_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            for obj in set_list:
                obj.process_tag = 0
                obj.save()
                logging(obj, user, LogSubUnitProject, "清除标记")
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def photo_import(self, request, *args, **kwargs):
        user = request.user
        files = request.FILES.getlist("files", None)
        id = request.data.get('id', None)
        if id:
            work_order = SubUnitProject.objects.filter(id=id)[0]
        else:
            data = {
                "error": "系统错误联系管理员，无法回传单据ID！"
            }
            return Response(data)
        log_file_names = []
        if files:
            prefix = "ut3s2/project/subunitproject"
            a_oss = AliyunOSS(prefix, files)
            file_urls = a_oss.upload()
            for obj in file_urls["urls"]:
                photo_order = SUPFiles()
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
            logging(work_order, user, LogSubUnitProject, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class SubUnitProjectDevelopViewset(viewsets.ModelViewSet):
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
    serializer_class = SubUnitProjectSerializer
    filter_class = SubUnitProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return SubUnitProject.objects.none()
        queryset = SubUnitProject.objects.filter(order_status=2).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 2
        f = SubUnitProjectFilter(params)
        serializer = SubUnitProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 2
        if all_select_tag:
            handle_list = SubUnitProjectFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = SubUnitProject.objects.filter(id__in=order_ids, order_status=2)
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
        if n:
            for obj in check_list:
                _q_component_project = obj.componentproject_set.all()
                if not _q_component_project.exists():
                    _q_productcore = ProductCore.objects.filter(product_line=obj.product_line, component_category__type=obj.type)
                    if _q_productcore.exists():
                        error_tag = 0
                        for c_category in _q_productcore:
                            component_order = Component()
                            component_order.category = c_category.component_category
                            preffix = re.sub("[\(（](.+?)[\)）]", "", str(c_category.component_category.name))
                            suffix_code = str(obj.unit_project.name.units.code)
                            preffix_code = str(obj.subunits_version.subunit.code)
                            component_order.name = "%s %s" % (preffix, suffix_code)
                            component_order.code = "%s-%s" % (preffix_code, str(c_category.component_category.code))
                            component_order.creator = user
                            try:
                                component_order.save()
                                logging(obj, user, LogSubUnitProject, "创建组项：%s" % component_order.name)
                            except Exception as e:
                                data["error"].append("%s 组项创建错误：%s" % (component_order.name, e))
                                error_tag = 1
                                continue
                            component_version = ComponentVersion()
                            suffix_version = "V001"
                            component_version.name = "%s %s" % (component_order.name, suffix_version)
                            component_version.code = "%s%s" % (component_order.code, suffix_version)
                            component_version.number = 1
                            component_version.component = component_order
                            component_version.creator = user
                            try:
                                component_version.save()
                                logging(obj, user, LogSubUnitProject, "创建组项版本：%s" % component_version.name)
                            except Exception as e:
                                data["error"].append("%s 组项版本创建错误： %s" % (component_version.name, e))
                                error_tag = 1
                                continue
                            component_project = ComponentProject()
                            component_project.category = obj.category
                            component_project.subunits_project = obj
                            component_project.product_line = obj.product_line
                            component_project.component_version = component_version
                            component_project.component_category = c_category.component_category
                            component_project.creator = user
                            try:
                                component_project.save()
                                logging(obj, user, LogSubUnitProject, "创建了组项项目：%s" % component_version.name)
                                logging(component_project, user, LogComponentProject, "创建")
                            except Exception as e:
                                data["error"].append("%s 组项项目创建错误： %s" % (component_version.name, e))
                                error_tag = 1
                                continue
                        if error_tag:
                            data["error"].append("%s 请检查错误，修复问题后，选择修复单据" % obj.id)
                            n -= 1
                            obj.mistake_tag = 3
                            obj.save()
                            continue
                    else:
                        data["error"].append("%s 产品线未查询到预制组件类型" % obj.id)
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                else:
                    exists_c_category = []
                    for obj_component in _q_component_project:
                        exists_c_category.append(obj_component.component_category)
                    _q_productcore = ProductCore.objects.filter(product_line=obj.product_line, component_category__type=obj.type)
                    if _q_productcore.exists():
                        error_tag = 0
                        for c_category in _q_productcore:
                            if c_category.component_category not in exists_c_category:
                                component_order = Component()
                                component_order.category = c_category.component_category
                                preffix = re.sub("[\(（](.+?)[\)）]", "", str(c_category.component_category.name))
                                suffix_code = str(obj.unit_project.name.units.code)
                                preffix_code = str(obj.subunits_version.subunit.code)
                                component_order.name = "%s %s" % (preffix, suffix_code)
                                component_order.code = "%s-%s" % (preffix_code, str(c_category.component_category.code))
                                component_order.creator = user
                                try:
                                    component_order.save()
                                    logging(obj, user, LogSubUnitProject, "创建组项：%s" % component_order.name)
                                except Exception as e:
                                    data["error"].append("%s 组项创建错误：%s" % (component_order.name, e))
                                    error_tag = 1
                                    continue
                                component_version = ComponentVersion()
                                suffix_version = "V001"
                                component_version.name = "%s %s" % (component_order.name, suffix_version)
                                component_version.code = "%s%s" % (component_order.code, suffix_version)
                                component_version.number = 1
                                component_version.component = component_order
                                component_version.creator = user
                                try:
                                    component_version.save()
                                    logging(obj, user, LogSubUnitProject, "创建组项版本：%s" % component_version.name)
                                except Exception as e:
                                    data["error"].append("%s 组项版本创建错误： %s" % (component_version.name, e))
                                    error_tag = 1
                                    continue
                                component_project = ComponentProject()
                                component_project.category = obj.category
                                component_project.subunits_project = obj
                                component_project.product_line = obj.product_line
                                component_project.component_version = component_version
                                component_project.component_category = c_category.component_category
                                component_project.creator = user
                                try:
                                    component_project.save()
                                    logging(obj, user, LogSubUnitProject, "创建了组项项目：%s" % component_version.name)
                                    logging(component_project, user, LogComponentProject, "创建")
                                except Exception as e:
                                    data["error"].append("%s 组项项目创建错误： %s" % (component_version.name, e))
                                    error_tag = 1
                                    continue
                        if error_tag:
                            data["error"].append("%s 请检查错误，修复问题后，选择修复单据" % obj.id)
                            n -= 1
                            obj.mistake_tag = 3
                            obj.save()
                            continue
                    else:
                        data["error"].append("%s 产品线未查询到预制组件类型" % obj.id)
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                obj.mistake_tag = 0
                obj.save()
                logging(obj, user, LogSubUnitProject, "确认项目单据")
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
            for obj in reject_list:
                obj.mogoods_set.all().delete()
            reject_list.update(order_status=0)
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def set_confirm(self, request, *args, **kwargs):
        params = request.data
        user = request.user
        set_list = self.get_handle_list(params)
        n = len(set_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            for obj in set_list:
                obj.process_tag = 1
                obj.save()
                logging(obj, user, LogSubUnitProject, "标记确认项目")
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def reset_tag(self, request, *args, **kwargs):
        params = request.data
        user = request.user
        set_list = self.get_handle_list(params)
        n = len(set_list)
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        if n:
            for obj in set_list:
                obj.process_tag = 0
                obj.save()
                logging(obj, user, LogSubUnitProject, "清除标记")
        else:
            raise serializers.ValidationError("没有可驳回的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def photo_import(self, request, *args, **kwargs):
        user = request.user
        files = request.FILES.getlist("files", None)
        id = request.data.get('id', None)
        if id:
            work_order = SubUnitProject.objects.filter(id=id)[0]
        else:
            data = {
                "error": "系统错误联系管理员，无法回传单据ID！"
            }
            return Response(data)
        log_file_names = []
        if files:
            prefix = "ut3s2/project/subunitproject"
            a_oss = AliyunOSS(prefix, files)
            file_urls = a_oss.upload()
            for obj in file_urls["urls"]:
                photo_order = SUPFiles()
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
            logging(work_order, user, LogSubUnitProject, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class SubUnitProjectViewset(viewsets.ModelViewSet):
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
    serializer_class = SubUnitProjectSerializer
    filter_class = SubUnitProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return SubUnitProject.objects.none()
        queryset = SubUnitProject.objects.filter(order_status=1).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["department"] = user.department
        params["order_status"] = 1
        f = SubUnitProjectFilter(params)
        serializer = SubUnitProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        department = self.request.user.department
        params["department"] = department
        if all_select_tag:
            handle_list = SubUnitProjectFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = SubUnitProject.objects.filter(id__in=order_ids, order_status=1)
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
                obj.mogoods_set.all().delete()
            reject_list.update(order_status=0)
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
            '店铺': 'shop',
            '客户网名': 'nickname',
            '收件人': 'receiver',
            '地址': 'address',
            '手机': 'mobile',
            '货品编码': 'goods_id',
            '数量': 'quantity',
            '单据类型': 'order_category',
            '机器序列号': 'm_sn',
            '故障部位': 'broken_part',
            '故障描述': 'description',
        }

        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ["店铺", "客户网名", "收件人", "地址", "手机", "货品编码", "货品名称", "数量", "单据类型",
                             "机器序列号", "故障部位", "故障描述"]

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
            _ret_verify_field = ManualOrder.verify_mandatory(columns_key)
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

            order_fields = ["nickname", "receiver", "address", "mobile", "m_sn", "broken_part", "description"]
            order = ManualOrder()
            for field in order_fields:
                setattr(order, field, row[field])
            order.order_category = category_dic.get(row["order_category"], None)
            _q_shop =  Shop.objects.filter(name=row["shop"])
            if _q_shop.exists():
                order.shop = _q_shop[0]

            _spilt_addr = PickOutAdress(str(order.address))
            _rt_addr = _spilt_addr.pickout_addr()
            if not isinstance(_rt_addr, dict):
                report_dic["error"].append("%s 地址无法提取省市区" % order.address)
                report_dic["false"] += 1
                continue
            cs_info_fields = ["province", "city", "district", "address"]
            for key_word in cs_info_fields:
                setattr(order, key_word, _rt_addr.get(key_word, None))

            try:
                order.creator = request.user.username
                order.save()
                report_dic["successful"] += 1
            except Exception as e:
                report_dic['error'].append("%s 保存出错" % row["nickname"])
                report_dic["false"] += 1
            goods_details = MOGoods()
            goods_details.manual_order = order
            goods_details.quantity = row["quantity"]
            _q_goods = Goods.objects.filter(goods_id=row["goods_id"])
            if _q_goods.exists():
                goods_details.goods_name = _q_goods[0]
                goods_details.goods_id = row["goods_id"]
            else:
                report_dic["error"].append("%s UT无此货品" % row["goods_id"])
                report_dic["false"] += 1
                continue
            try:
                goods_details.creator = request.user.username
                goods_details.save()
            except Exception as e:
                report_dic['error'].append("%s 保存明细出错" % row["nickname"])
        return report_dic


class SUPFilesViewset(viewsets.ModelViewSet):
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
    serializer_class = SUPFilesSerializer
    filter_class = SUPFilesFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return SUPFiles.objects.none()
        queryset = SUPFiles.objects.all().order_by("id")
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
            photo_order = SUPFiles.objects.filter(id=id, creator=user, is_delete=False)
            if photo_order.exists():
                photo_order = photo_order[0]
                photo_order.is_delete = 1
                photo_order.save()
                data["successful"] += 1
                logging(photo_order.workorder, user, LogSubUnitProject, "删除图片：%s" % photo_order.name)
            else:
                data["false"] += 1
                data["error"].append("只有创建者才有删除权限")
        else:
            data["false"] += 1
            data["error"].append("没有找到删除对象")
        return Response(data)



