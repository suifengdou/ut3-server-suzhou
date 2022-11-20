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
from .models import PhototypeProject, PhototypeProjectDetails, LogPhototypeProject, LogPhototypeProjectDetails, PTFiles
from .serializers import PhototypeProjectSerializer, PhototypeProjectDetailsSerializer, PTFilesSerializer
from .filters import PhototypeProjectFilter, PhototypeProjectDetailsFilter, PTFilesFilter
from apps.utils.geography.models import City, District
from apps.utils.logging.loggings import logging, getlogs, getfiles
from apps.utils.oss.aliyunoss import AliyunOSS
from ut3forsuzhou.settings import EXPORT_TOPLIMIT
from apps.project.phototypeexecuteproject.models import PhototypeExecuteProject, PhototypeExecuteProjectDetails, LogPhototypeExecuteProject, LogPhototypeExecuteProjectDetails


class PhototypeProjectPrepareViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeProjectSerializer
    filter_class = PhototypeProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeProject.objects.none()
        queryset = PhototypeProject.objects.filter(order_status=1).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 1
        f = PhototypeProjectFilter(params)
        serializer = PhototypeProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeProject, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        department = self.request.user.department
        params["department"] = department
        if all_select_tag:
            handle_list = PhototypeProjectFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeProject.objects.filter(id__in=order_ids, order_status=1)
            else:
                handle_list = []
        return handle_list

    @action(methods=['patch'], detail=False)
    def check(self, request, *args, **kwargs):
        user = self.request.user
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
                if obj.process_tag != 1:
                    data["error"].append("%s未标记单据不可确认" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 1
                    obj.save()
                    continue

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.save()
                logging(obj, user, LogPhototypeProject, "确认组项项目")
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
                _q_check_order = obj.phototypeexecuteproject_set.all().filter(order_status__in=[1, 2])
                if len(_q_check_order) > 0:
                    data["error"].append("%s 已存在执行单不可驳回" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 1
                    obj.save()
                    continue
                _q_delete_order = obj.phototypeprojectdetails_set.all()
                if _q_delete_order.exists():
                    _q_delete_order.delete()
                    logging(obj, user, LogPhototypeProject, "清除了所有手板项目明细")

                c_time = datetime.datetime.now()
                c_time = re.sub("[ :\.-]", "", str(c_time))
                obj.name = "%s-%s-取消" % (obj.name, c_time)
                obj.code = "%s-%s-CANCEL" % (obj.code, c_time)
                obj.order_status = 0
                obj.save()
                logging(obj, user, LogPhototypeProject, "取消了手板项目单")
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
                logging(obj, user, LogPhototypeProject, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeProject, "预备阶段清除标记")
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
            work_order = PhototypeProject.objects.filter(id=id)[0]
        else:
            data = {
                "error": "系统错误联系管理员，无法回传单据ID！"
            }
            return Response(data)
        log_file_names = []
        if files:
            prefix = "ut3s2/project/phototype"
            a_oss = AliyunOSS(prefix, files)
            file_urls = a_oss.upload()
            for obj in file_urls["urls"]:
                photo_order = PTFiles()
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
            logging(work_order, user, LogPhototypeProject, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class PhototypeProjectDevelopViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeProjectSerializer
    filter_class = PhototypeProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeProject.objects.none()
        queryset = PhototypeProject.objects.filter(order_status=2).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 2
        f = PhototypeProjectFilter(params)
        serializer = PhototypeProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeProject, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 2
        department = self.request.user.department
        params["department"] = department
        if all_select_tag:
            handle_list = PhototypeProjectFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeProject.objects.filter(id__in=order_ids, order_status=2)
            else:
                handle_list = []
        return handle_list

    @action(methods=['patch'], detail=False)
    def check(self, request, *args, **kwargs):
        user = self.request.user
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
                if obj.process_tag != 1:
                    data["error"].append("%s未标记单据不可确认" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 1
                    obj.save()
                    continue

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.save()
                logging(obj, user, LogPhototypeProject, "确认组项项目")
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
                logging(obj, user, LogPhototypeProject, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeProject, "预备阶段清除标记")
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
            work_order = PhototypeProject.objects.filter(id=id)[0]
        else:
            data = {
                "error": "系统错误联系管理员，无法回传单据ID！"
            }
            return Response(data)
        log_file_names = []
        if files:
            prefix = "ut3s2/project/phototype"
            a_oss = AliyunOSS(prefix, files)
            file_urls = a_oss.upload()
            for obj in file_urls["urls"]:
                photo_order = PTFiles()
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
            logging(work_order, user, LogPhototypeProject, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class PhototypeProjectViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeProjectSerializer
    filter_class = PhototypeProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeProject.objects.none()
        queryset = PhototypeProject.objects.all().order_by("-id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        f = PhototypeProjectFilter(params)
        serializer = PhototypeProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = PhototypeProject.objects.filter(id=id)[0]
        ret = getlogs(instance, LogPhototypeProject)
        return Response(ret)

    @action(methods=['patch'], detail=False)
    def get_file_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = PhototypeProject.objects.filter(id=id)[0]
        ret = getfiles(instance, PTFiles)
        return Response(ret)


class PhototypeProjectDetailsMakeViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeProjectDetailsSerializer
    filter_class = PhototypeProjectDetailsFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeProjectDetails.objects.none()
        queryset = PhototypeProjectDetails.objects.filter(order_status=1, is_making=True).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 1
        params["is_making"] = True
        f = PhototypeProjectDetailsFilter(params)
        serializer = PhototypeProjectDetailsSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeProjectDetails, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        params["is_making"] = True
        if all_select_tag:
            handle_list = PhototypeProjectDetailsFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeProjectDetails.objects.filter(id__in=order_ids, order_status=1, is_making=True)
            else:
                handle_list = []
        return handle_list

    @action(methods=['patch'], detail=False)
    def check(self, request, *args, **kwargs):
        user = self.request.user
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
                if not obj.group_code:
                    data["error"].append("%s 未设置分组标识不可递交" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 1
                    obj.save()
                    continue
                try:
                    phototype_execute_project_details = obj.phototypeexecuteprojectdetails
                    if phototype_execute_project_details.order_status != 0:
                        data["error"].append("%s 系统逻辑错误，请联系管理员处理" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                    else:
                        phototype_execute_project_details.order_status = 1

                except:
                    phototype_execute_project_details = PhototypeExecuteProjectDetails()
                _q_phototype_execute_project = PhototypeExecuteProject.objects.filter(
                    phototype_project=obj.phototype_project, group_code=obj.group_code)
                if _q_phototype_execute_project.exists():
                    phototype_execute_project = _q_phototype_execute_project[0]
                    if phototype_execute_project.order_status == 0:
                        phototype_execute_project.order_status = 1
                    elif phototype_execute_project.order_status > 1:
                        data["error"].append("%s 同组标识手板执行单已经在开发，请驳回，再递交" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 3
                        obj.save()
                        continue
                else:
                    phototype_execute_project = PhototypeExecuteProject()
                _pep_order_fields = ["category", "product_line", "subunit_project", "type", "memo"]
                for _pep_keyword in _pep_order_fields:
                    setattr(phototype_execute_project, _pep_keyword, getattr(obj.phototype_project, _pep_keyword, None))
                phototype_execute_project.group_code = obj.group_code
                phototype_execute_project.phototype_project = obj.phototype_project
                phototype_execute_project.is_making = False
                phototype_execute_project.name = "%s-%s" % (obj.phototype_project.name, str(obj.group_code))
                phototype_execute_project.code = "%s-%s" % (obj.phototype_project.code, str(obj.group_code))
                phototype_execute_project.creator = user
                try:
                    phototype_execute_project.save()
                    logging(phototype_execute_project, user, LogPhototypeExecuteProject, "基于 %s 创建并更新" % str(obj.name))
                except Exception as e:
                    data["error"].append("%s 创建或归属执行单错误：%s(请把此内容截大图发管理员)" % (str(obj.id), e))
                    n -= 1
                    obj.mistake_tag = 4
                    obj.save()
                    continue
                phototype_execute_project_details.phototype_execute_project = phototype_execute_project
                phototype_execute_project_details.phototype_project_details = obj
                _pepd_order_fields = ["name", "file_name", "code", "initial_part", "product_line", "subunit_project",
                                      "component_project", "component_code", "category", "diagram_number",
                                      "specification", "technology", "material", "shrinkage", "material_color_number",
                                      "quantity", "weight", "is_lacquered", "is_group", "color_number", "group_code",
                                      "is_making", "memo"]
                for _pepd_keyword in _pepd_order_fields:
                    setattr(phototype_execute_project_details, _pepd_keyword, getattr(obj, _pepd_keyword, None))
                phototype_execute_project_details.creator = user
                try:
                    phototype_execute_project_details.save()
                    logging(phototype_execute_project_details, user, LogPhototypeExecuteProjectDetails, "创建")
                except Exception as e:
                    data["error"].append(f'{str(obj.id)} 创建或更新执行单明细错误：{e}(请把此内容截大图发管理员)')
                    n -= 1
                    obj.mistake_tag = 5
                    obj.save()
                    continue

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.save()
                logging(obj, user, LogPhototypeProjectDetails, "递交成功")
                _q_check_details = obj.phototype_project.phototypeprojectdetails_set.all().filter(order_status=1)
                if len(_q_check_details) == 0:
                    obj.phototype_project.order_status = 2
                    obj.phototype_project.save()
                    logging(obj.phototype_project, user, LogPhototypeProject, "自动审核项目单")
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
                logging(obj, user, LogPhototypeProject, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeProject, "预备阶段清除标记")
        else:
            raise serializers.ValidationError("没有可清除的单据！")
        data["successful"] = n
        return Response(data)


class PhototypeProjectDetailsPurchaseViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeProjectDetailsSerializer
    filter_class = PhototypeProjectDetailsFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeProjectDetails.objects.none()
        queryset = PhototypeProjectDetails.objects.filter(order_status=1, is_making=False).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 1
        params["is_making"] = True
        f = PhototypeProjectDetailsFilter(params)
        serializer = PhototypeProjectDetailsSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeProjectDetails, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        params["is_making"] = True
        if all_select_tag:
            handle_list = PhototypeProjectDetailsFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeProjectDetails.objects.filter(id__in=order_ids, order_status=1, is_making=False)
            else:
                handle_list = []
        return handle_list

    @action(methods=['patch'], detail=False)
    def check(self, request, *args, **kwargs):
        user = self.request.user
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
                if not obj.group_code:
                    data["error"].append("%s 未设置分组标识不可递交" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 1
                    obj.save()
                    continue
                try:
                    phototype_execute_project_details = obj.phototypeexecuteprojectdetails
                    if phototype_execute_project_details.order_status != 0:
                        data["error"].append("%s 系统逻辑错误，请联系管理员处理" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                    else:
                        phototype_execute_project_details.order_status = 1

                except:
                    phototype_execute_project_details = PhototypeExecuteProjectDetails()
                _q_phototype_execute_project = PhototypeExecuteProject.objects.filter(phototype_project=obj.phototype_project, group_code=obj.group_code)
                if _q_phototype_execute_project.exists():
                    phototype_execute_project = _q_phototype_execute_project[0]
                    if phototype_execute_project.order_status == 0:
                        phototype_execute_project.order_status = 1
                    elif phototype_execute_project.order_status > 1:
                        data["error"].append("%s 同组标识手板执行单已经在开发，请驳回，再递交" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 3
                        obj.save()
                        continue
                else:
                    phototype_execute_project = PhototypeExecuteProject()
                _pep_order_fields = ["category", "product_line", "subunit_project", "type", "memo"]
                for _pep_keyword in _pep_order_fields:
                    setattr(phototype_execute_project, _pep_keyword, getattr(obj.phototype_project, _pep_keyword, None))
                phototype_execute_project.group_code = obj.group_code
                phototype_execute_project.phototype_project = obj.phototype_project
                phototype_execute_project.is_making = True
                phototype_execute_project.name = "%s-%s" % (obj.phototype_project.name, str(obj.group_code))
                phototype_execute_project.code = "%s-%s" % (obj.phototype_project.code, str(obj.group_code))
                phototype_execute_project.creator = user
                try:
                    phototype_execute_project.save()
                    logging(phototype_execute_project, user, LogPhototypeExecuteProject, "基于 %s 创建并更新" % str(obj.name) )
                except Exception as e:
                    data["error"].append("%s 创建或归属执行单错误：%s(请把此内容截大图发管理员)" % (str(obj.id), e))
                    n -= 1
                    obj.mistake_tag = 4
                    obj.save()
                    continue
                phototype_execute_project_details.phototype_execute_project = phototype_execute_project
                phototype_execute_project_details.phototype_project_details = obj
                _pepd_order_fields = ["name", "file_name", "code", "initial_part", "product_line", "subunit_project",
                                      "component_project", "component_code", "category", "diagram_number",
                                      "specification", "technology", "material", "shrinkage", "material_color_number",
                                      "quantity", "weight", "is_lacquered", "is_group", "color_number", "group_code",
                                      "is_making", "memo"]
                for _pepd_keyword in _pepd_order_fields:
                    setattr(phototype_execute_project_details, _pepd_keyword, getattr(obj, _pepd_keyword, None))
                phototype_execute_project_details.creator = user
                try:
                    phototype_execute_project_details.save()
                    logging(phototype_execute_project_details, user, LogPhototypeExecuteProjectDetails, "创建")
                except Exception as e:
                    data["error"].append(f'{str(obj.id)} 创建或更新执行单明细错误：{e}(请把此内容截大图发管理员)')
                    n -= 1
                    obj.mistake_tag = 5
                    obj.save()
                    continue

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.save()
                logging(obj, user, LogPhototypeProjectDetails, "递交成功")
                _q_check_details = obj.phototype_project.phototypeprojectdetails_set.all().filter(order_status=1)
                if len(_q_check_details) == 0:
                    obj.phototype_project.order_status = 2
                    obj.phototype_project.save()
                    logging(obj.phototype_project, user, LogPhototypeProject, "自动审核项目单")
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
                logging(obj, user, LogPhototypeProject, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeProject, "预备阶段清除标记")
        else:
            raise serializers.ValidationError("没有可清除的单据！")
        data["successful"] = n
        return Response(data)


class PhototypeProjectDetailsViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeProjectDetailsSerializer
    filter_class = PhototypeProjectDetailsFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeProjectDetails.objects.none()
        queryset = PhototypeProjectDetails.objects.all().order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        f = PhototypeProjectDetailsFilter(params)
        serializer = PhototypeProjectDetailsSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeProjectDetails, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        if all_select_tag:
            handle_list = PhototypeProjectDetailsFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeProjectDetails.objects.filter(id__in=order_ids, order_status=1)
            else:
                handle_list = []
        return handle_list

    @action(methods=['patch'], detail=False)
    def check(self, request, *args, **kwargs):
        user = self.request.user
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
                if obj.process_tag != 1:
                    data["error"].append("%s未标记单据不可确认" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 1
                    obj.save()
                    continue

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.save()
                logging(obj, user, LogPhototypeProject, "确认组项项目")
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
                logging(obj, user, LogPhototypeProject, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeProject, "预备阶段清除标记")
        else:
            raise serializers.ValidationError("没有可清除的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = PhototypeProjectDetails.objects.filter(id=id)[0]
        ret = getlogs(instance, LogPhototypeProjectDetails)
        return Response(ret)


class PTFilesViewset(viewsets.ModelViewSet):
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
    serializer_class = PTFilesSerializer
    filter_class = PTFilesFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PTFiles.objects.none()
        queryset = PTFiles.objects.all().order_by("id")
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
            photo_order = PTFiles.objects.filter(id=id, creator=user, is_delete=False)
            if photo_order.exists():
                photo_order = photo_order[0]
                photo_order.is_delete = 1
                photo_order.save()
                data["successful"] += 1
                logging(photo_order.workorder, user, LogPhototypeProject, "删除文档：%s" % photo_order.name)
            else:
                data["false"] += 1
                data["error"].append("只有创建者才有删除权限")
        else:
            data["false"] += 1
            data["error"].append("没有找到删除对象")
        return Response(data)



