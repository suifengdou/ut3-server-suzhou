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
from django.db.models import Avg,Sum,Max,Min
from rest_framework.permissions import IsAuthenticated
from ut3forsuzhou.permissions import Permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from .models import PhototypeExecuteProject, PhototypeExecuteProjectDetails, LogPhototypeExecuteProject, \
    LogPhototypeExecuteProjectDetails, PTEFiles
from .serializers import PhototypeExecuteProjectSerializer, PhototypeExecuteProjectDetailsSerializer, PTEFilesSerializer
from .filters import PhototypeExecuteProjectFilter, PhototypeExecuteProjectDetailsFilter, PTEFilesFilter
from apps.utils.logging.loggings import logging, getlogs, getfiles
from apps.utils.oss.aliyunoss import AliyunOSS
from ut3forsuzhou.settings import EXPORT_TOPLIMIT
from apps.statement.phototypestatement.models import PhototypeExecuteProjectStatement, LogPhototypeExecuteProjectStatement
from apps.project.phototypeproject.models import LogPhototypeProjectDetails


class PhototypeExecuteProjectPrepareViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeExecuteProjectSerializer
    filter_class = PhototypeExecuteProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeExecuteProject.objects.none()
        queryset = PhototypeExecuteProject.objects.filter(order_status=1).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 1
        f = PhototypeExecuteProjectFilter(params)
        serializer = PhototypeExecuteProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeExecuteProject, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        department = self.request.user.department
        params["department"] = department
        if all_select_tag:
            handle_list = PhototypeExecuteProjectFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeExecuteProject.objects.filter(id__in=order_ids, order_status=1)
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
                obj.settle_amount = obj.amount - obj.adjust_amount
                _q_statement_order = PhototypeExecuteProjectStatement.objects.filter(project=obj)
                if _q_statement_order.exists():
                    statement_order = _q_statement_order[0]
                    if statement_order.order_status == 0:
                        statement_order.order_status = 1
                    else:
                        data["error"].append("%s已存在结算单，请联系管理员处理" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                else:
                    statement_order = PhototypeExecuteProjectStatement()
                order_fileds = ["name", "code", "amount", "adjust_amount", "settle_amount", "remaining", "is_making", "memo"]
                for key_word in order_fileds:
                    setattr(statement_order, key_word, getattr(obj, key_word, None))
                statement_order.supplier = obj.phototype_supplier
                statement_order.project = obj
                statement_order.creator = user
                statement_order.remaining = obj.settle_amount
                try:
                    statement_order.save()
                    logging(statement_order, user, LogPhototypeExecuteProjectStatement, "创建")
                    logging(obj, user, LogPhototypeExecuteProject, "创建了结算单%s" % str(statement_order.code))
                except Exception as e:
                    data["error"].append("%s结算单创建错误：%s" % (str(obj.id), e))
                    n -= 1
                    obj.mistake_tag = 3
                    obj.save()
                    continue
                obj.order_status = 2
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.save()
                logging(obj, user, LogPhototypeExecuteProject, "确认组项项目")
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
                if obj.phototype_project.order_status != 1:
                    data["error"].append("%s项目单状态不是准备状态不可驳回" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 5
                    obj.save()
                    continue
                all_details = obj.phototypeexecuteprojectdetails_set.all()
                for detail in all_details:
                    detail.phototype_project_details.order_status = 1
                    detail.phototype_project_details.save()
                    logging(detail.phototype_project_details, user, LogPhototypeProjectDetails, "驳回到准备状态")
                    detail.order_status = 0
                    detail.save()
                    logging(detail, user, LogPhototypeExecuteProjectDetails, "取消明细单")
                obj.order_status = 0
                obj.save()
                logging(obj, user, LogPhototypeExecuteProject, "取消执行单")
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
                logging(obj, user, LogPhototypeExecuteProject, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeExecuteProject, "预备阶段清除标记")
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
            work_order = PhototypeExecuteProject.objects.filter(id=id)[0]
        else:
            data = {
                "error": "系统错误联系管理员，无法回传单据ID！"
            }
            return Response(data)
        log_file_names = []
        if files:
            prefix = "ut3s2/project/component"
            a_oss = AliyunOSS(prefix, files)
            file_urls = a_oss.upload()
            for obj in file_urls["urls"]:
                photo_order = PTEFiles()
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
            logging(work_order, user, LogPhototypeExecuteProject, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class PhototypeExecuteProjectDevelopViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeExecuteProjectSerializer
    filter_class = PhototypeExecuteProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeExecuteProject.objects.none()
        queryset = PhototypeExecuteProject.objects.filter(order_status=2).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 2
        f = PhototypeExecuteProjectFilter(params)
        serializer = PhototypeExecuteProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeExecuteProject, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 2
        department = self.request.user.department
        if all_select_tag:
            handle_list = PhototypeExecuteProjectFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeExecuteProject.objects.filter(id__in=order_ids, order_status=2)
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
                logging(obj, user, LogPhototypeExecuteProject, "确认组项项目")
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
                if obj.phototypeexecuteprojectstatement.order_status > 1:
                    data["error"].append("%s结算单已审核不可驳回" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 4
                    obj.save()
                    continue
                obj.phototypeexecuteprojectstatement.order_status = 0
                obj.phototypeexecuteprojectstatement.save()
                logging(obj.phototypeexecuteprojectstatement, user, LogPhototypeExecuteProjectStatement, "取消")
                obj.order_status = 1
                all_details = obj.phototypeexecuteprojectdetails_set.all()
                for detail in all_details:
                    detail.order_status = 1
                    detail.save()
                    logging(detail, user, LogPhototypeExecuteProjectDetails, "驳回到准备状态")
                obj.save()
                logging(obj, user, LogPhototypeExecuteProject, "驳回执行单到准备")
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
                logging(obj, user, LogPhototypeExecuteProject, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeExecuteProject, "预备阶段清除标记")
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
            work_order = PhototypeExecuteProject.objects.filter(id=id)[0]
        else:
            data = {
                "error": "系统错误联系管理员，无法回传单据ID！"
            }
            return Response(data)
        log_file_names = []
        if files:
            prefix = "ut3s2/project/component"
            a_oss = AliyunOSS(prefix, files)
            file_urls = a_oss.upload()
            for obj in file_urls["urls"]:
                photo_order = PTEFiles()
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
            logging(work_order, user, LogPhototypeExecuteProject, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class PhototypeExecuteProjectViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeExecuteProjectSerializer
    filter_class = PhototypeExecuteProjectFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeExecuteProject.objects.none()
        queryset = PhototypeExecuteProject.objects.all().order_by("-id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        f = PhototypeExecuteProjectFilter(params)
        serializer = PhototypeExecuteProjectSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = PhototypeExecuteProject.objects.filter(id=id)[0]
        ret = getlogs(instance, LogPhototypeExecuteProject)
        return Response(ret)

    @action(methods=['patch'], detail=False)
    def get_file_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = PhototypeExecuteProject.objects.filter(id=id)[0]
        ret = getfiles(instance, PTEFiles)
        return Response(ret)


class PhototypeExecuteProjectDetailsPrepareViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeExecuteProjectDetailsSerializer
    filter_class = PhototypeExecuteProjectDetailsFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeExecuteProjectDetails.objects.none()
        queryset = PhototypeExecuteProjectDetails.objects.filter(order_status=1).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 1
        f = PhototypeExecuteProjectDetailsFilter(params)
        serializer = PhototypeExecuteProjectDetailsSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeExecuteProjectDetails, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        if all_select_tag:
            handle_list = PhototypeExecuteProjectDetailsFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeExecuteProjectDetails.objects.filter(id__in=order_ids, order_status=1)
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
                if obj.price == 0:
                    if obj.process_tag != 9:
                        data["error"].append("%s单价为零无特殊标记不可审核" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                phototype_execute_project = obj.phototype_execute_project
                phototype_execute_project.amount = obj.phototype_execute_project.amount + obj.amount
                phototype_execute_project.save()
                logging(phototype_execute_project, user, LogPhototypeExecuteProject, "合计金额增加：%s" % obj.amount)
                _q_check_all_details = PhototypeExecuteProjectDetails.objects.filter(phototype_execute_project=phototype_execute_project, order_status=1)
                if len(_q_check_all_details) == 1:
                    total_amount = phototype_execute_project.phototypeexecuteprojectdetails_set.all().aggregate(Sum("amount"))["amount__sum"]
                    if total_amount != phototype_execute_project.amount:
                        phototype_execute_project.amount = total_amount
                    phototype_execute_project.process_tag = 1
                    phototype_execute_project.save()

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.save()
                logging(obj, user, LogPhototypeExecuteProjectDetails, "审核手板执行单明细")
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
                logging(obj, user, LogPhototypeExecuteProjectDetails, "预备阶段标记确认项目")
        else:
            raise serializers.ValidationError("没有可确认的单据！")
        data["successful"] = n
        return Response(data)

    @action(methods=['patch'], detail=False)
    def set_special(self, request, *args, **kwargs):
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
                obj.process_tag = 9
                obj.save()
                logging(obj, user, LogPhototypeExecuteProjectDetails, "预备阶段标记特殊")
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
                logging(obj, user, LogPhototypeExecuteProjectDetails, "预备阶段清除标记")
        else:
            raise serializers.ValidationError("没有可清除的单据！")
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
            "ID": "id",
            "单价": "price",
        }

        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ["ID", "单价"]

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
            _ret_verify_field = PhototypeExecuteProjectDetails.verify_mandatory(columns_key)
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
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}
        for row in resource:
            _q_pep_detials = PhototypeExecuteProjectDetails.objects.filter(id=row["id"], order_status=1)
            if _q_pep_detials.exists():
                pep_detials = _q_pep_detials[0]
            else:
                report_dic["error"].append("%s 准备状态中无此明细" % row["id"])
                report_dic["false"] += 1
                continue

            if row["price"] and int(row["price"]) > 0 and int(row["price"]) != pep_detials.price:
                pep_detials.price = int(row["price"])
                pep_detials.amount = pep_detials.price * pep_detials.quantity
            else:
                report_dic["error"].append("%s 价格为空或者价格错误或者价格是原价格" % row["id"])
                report_dic["false"] += 1
                continue
            try:
                pep_detials.save()
                report_dic["successful"] += 1
                logging(pep_detials, user, LogPhototypeExecuteProjectDetails, "更新完导入价格：%s" % pep_detials.price)
            except Exception as e:
                report_dic["error"].append("%s 更新价格失败：%s" % (row["id"], str(e)))
                report_dic["false"] += 1

        return report_dic


class PhototypeExecuteProjectDetailsMakeViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeExecuteProjectDetailsSerializer
    filter_class = PhototypeExecuteProjectDetailsFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeExecuteProjectDetails.objects.none()
        queryset = PhototypeExecuteProjectDetails.objects.filter(order_status=2, is_making=True).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 2
        params["is_making"] = True
        f = PhototypeExecuteProjectDetailsFilter(params)
        serializer = PhototypeExecuteProjectDetailsSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeExecuteProjectDetails, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 2
        params["is_making"] = True
        if all_select_tag:
            handle_list = PhototypeExecuteProjectDetailsFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeExecuteProjectDetails.objects.filter(id__in=order_ids, order_status=2, is_making=True)
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
                logging(obj, user, LogPhototypeExecuteProject, "确认组项项目")
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
                logging(obj, user, LogPhototypeExecuteProject, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeExecuteProject, "预备阶段清除标记")
        else:
            raise serializers.ValidationError("没有可清除的单据！")
        data["successful"] = n
        return Response(data)


class PhototypeExecuteProjectDetailsPurchaseViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeExecuteProjectDetailsSerializer
    filter_class = PhototypeExecuteProjectDetailsFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeExecuteProjectDetails.objects.none()
        queryset = PhototypeExecuteProjectDetails.objects.filter(order_status=2, is_making=False).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 2
        params["is_making"] = False
        f = PhototypeExecuteProjectDetailsFilter(params)
        serializer = PhototypeExecuteProjectDetailsSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeExecuteProjectDetails, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 2
        params["is_making"] = False
        if all_select_tag:
            handle_list = PhototypeExecuteProjectDetailsFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeExecuteProjectDetails.objects.filter(id__in=order_ids, order_status=2, is_making=False)
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
                logging(obj, user, LogPhototypeExecuteProject, "确认组项项目")
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
                logging(obj, user, LogPhototypeExecuteProject, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeExecuteProject, "预备阶段清除标记")
        else:
            raise serializers.ValidationError("没有可清除的单据！")
        data["successful"] = n
        return Response(data)


class PhototypeExecuteProjectDetailsViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeExecuteProjectDetailsSerializer
    filter_class = PhototypeExecuteProjectDetailsFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeExecuteProjectDetails.objects.none()
        queryset = PhototypeExecuteProjectDetails.objects.all().order_by("-id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        f = PhototypeExecuteProjectDetailsFilter(params)
        serializer = PhototypeExecuteProjectDetailsSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeExecuteProjectDetails, "导出")
        return Response(serializer.data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = PhototypeExecuteProjectDetails.objects.filter(id=id)[0]
        ret = getlogs(instance, LogPhototypeExecuteProjectDetails)
        return Response(ret)


class PTEFilesViewset(viewsets.ModelViewSet):
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
    serializer_class = PTEFilesSerializer
    filter_class = PTEFilesFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PTEFiles.objects.none()
        queryset = PTEFiles.objects.all().order_by("id")
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
            photo_order = PTEFiles.objects.filter(id=id, creator=user, is_delete=False)
            if photo_order.exists():
                photo_order = photo_order[0]
                photo_order.is_delete = 1
                photo_order.save()
                data["successful"] += 1
                logging(photo_order.workorder, user, LogPhototypeExecuteProject, "删除文档：%s" % photo_order.name)
            else:
                data["false"] += 1
                data["error"].append("只有创建者才有删除权限")
        else:
            data["false"] += 1
            data["error"].append("没有找到删除对象")
        return Response(data)

