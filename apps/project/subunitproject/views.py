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
from ut3forsuzhou.settings import EXPORT_TOPLIMIT
from apps.utils.logging.loggings import logging, getlogs, getfiles
from apps.project.componentproject.models import ComponentProject, LogComponentProject
from apps.bom.component.models import Component, ComponentVersion
from apps.bom.productcore.models import ProductCore
from apps.project.phototypeproject.models import PhototypeProject, PhototypeProjectDetails, LogPhototypeProject, LogPhototypeProjectDetails


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
                            suffix_code = str(obj.unit_project.units_version.units.code)
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
                            component_project.subunit_project = obj
                            component_project.product_line = obj.product_line
                            component_project.component_version = component_version
                            component_project.component_category = c_category.component_category
                            component_project.name = component_version.name
                            component_project.code = component_version.code
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
        user = request.user
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
                logging(obj, user, LogSubUnitProject, "驳回项目")
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
            raise serializers.ValidationError("没有可确认的单据！")
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
            raise serializers.ValidationError("没有可清除的单据！")
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
    def create_phototype(self, request, *args, **kwargs):
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        user = request.user
        id = request.data.get("id", None)
        quantity = request.data.get("quantity", None)
        if not all([id, quantity]):
            data["error"].append("%s 未提交申请数量" )
            data["false"] = 1
            return Response(data)
        _q_subunit_project = SubUnitProject.objects.filter(id=id, order_status=2)
        if _q_subunit_project.exists():
            obj = _q_subunit_project[0]
        else:
            data["error"].append("%s 未查询到子项目")
            data["false"] = 1
            return Response(data)
        for component_project in obj.componentproject_set.all():
            if not component_project.initialpartproject_set.all().exists():
                data["error"].append("%s 存在空组项" % obj.id)
                data["false"] = 1
                obj.mistake_tag = 4
                obj.save()
                return Response(data)
        if obj.oriinitialpartproject_set.all().filter(order_status=1):
            data["error"].append("%s 存在未递交原初物料" % obj.id)
            data["false"] = 1
            obj.mistake_tag = 5
            obj.save()
            return Response(data)

        phototype_project_order = PhototypeProject()
        all_phototype_project = obj.phototypeproject_set.all()
        phototype_project_order.number = len(all_phototype_project) + 1
        phototype_project_order.subunit_project = obj
        _pp_order_fileds = ["product_line", "type"]
        for _pp_keyword in _pp_order_fileds:
            setattr(phototype_project_order, _pp_keyword, getattr(obj, _pp_keyword, None))
        phototype_project_order.code = "%s-P%s" % (obj.code, phototype_project_order.number)
        phototype_project_order.name = "%s第%s次手板" % (obj.name, phototype_project_order.number)
        phototype_project_order.creator = user
        phototype_project_order.quantity = int(quantity)
        try:
            phototype_project_order.save()
            logging(obj, user, LogSubUnitProject, "创建手板项目%s" % phototype_project_order.name)
            logging(phototype_project_order, user, LogPhototypeProject, "创建")
        except Exception as e:
            data["error"].append("%s 创建手板项目失败: %s" % (str(obj.id), e))
            data["false"] = 1
            obj.mistake_tag = 6
            obj.save()
            return Response(data)
        _q_initial_parts = obj.initialpartproject_set.all().exclude(order_status=0)
        __ppd_order_fields = ["name", "file_name", "code", "initial_part", "product_line", "subunit_project",
                              "component_project", "component_code", "category", "diagram_number",
                              "specification", "technology", "material", "shrinkage", "material_color_number",
                              "weight", "is_lacquered", "is_group", "color_number", "group_code", "is_making"]
        details_error_tag = 0
        for initial_part in _q_initial_parts:
            phototype_project_details_order = PhototypeProjectDetails()
            for _ppd_key_word in __ppd_order_fields:
                setattr(phototype_project_details_order, _ppd_key_word, getattr(initial_part, _ppd_key_word, None))
            phototype_project_details_order.phototype_project = phototype_project_order
            phototype_project_details_order.creator = user
            phototype_project_details_order.quantity = int(initial_part.quantity) * int(phototype_project_order.quantity)
            try:
                phototype_project_details_order.save()
                logging(obj, user, LogSubUnitProject, "创建手板项目%s" % phototype_project_details_order.name)
                logging(phototype_project_details_order, user, LogPhototypeProjectDetails, "创建")
            except Exception as e:
                data["error"].append("%s 创建手板项目失败: %s" % (str(obj.id), e))
                details_error_tag = 1
                break
        if details_error_tag:
            data["error"].append("%s 创建手板项目明细失败: %s" % (str(obj.id), e))
            data["false"] = 1
            obj.mistake_tag = 7
            obj.save()
            return Response(data)
        data["successful"] = 1
        obj.mistake_tag = 0
        obj.save()

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
            pass
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
        queryset = SubUnitProject.objects.all().order_by("-id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        f = SubUnitProjectFilter(params)
        serializer = SubUnitProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = SubUnitProject.objects.filter(id=id)[0]
        ret = getlogs(instance, LogSubUnitProject)
        return Response(ret)

    @action(methods=['patch'], detail=False)
    def get_file_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = SubUnitProject.objects.filter(id=id)[0]
        ret = getfiles(instance, SUPFiles)
        return Response(ret)


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
                logging(photo_order.workorder, user, LogSubUnitProject, "删除文档：%s" % photo_order.name)
            else:
                data["false"] += 1
                data["error"].append("只有创建者才有删除权限")
        else:
            data["false"] += 1
            data["error"].append("没有找到删除对象")
        return Response(data)



