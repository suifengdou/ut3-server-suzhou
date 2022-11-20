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
from .models import PhototypeExecuteProjectStatement, LogPhototypeExecuteProjectStatement
from .serializers import PhototypeExecuteProjectStatementSerializer
from .filters import PhototypeExecuteProjectStatementFilter
from apps.utils.geography.models import City, District
from apps.utils.logging.loggings import logging, getlogs, getfiles
from apps.utils.oss.aliyunoss import AliyunOSS
from apps.settle.payment.models import PaymentOrder, RelationPEPSToPay, LogPaymentOrder, LogRelationPEPSToPay
from ut3forsuzhou.settings import EXPORT_TOPLIMIT


class PhototypeExecuteProjectStatementSubmitViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeExecuteProjectStatementSerializer
    filter_class = PhototypeExecuteProjectStatementFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeExecuteProjectStatement.objects.none()
        queryset = PhototypeExecuteProjectStatement.objects.filter(order_status=1).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 1
        f = PhototypeExecuteProjectStatementFilter(params)
        serializer = PhototypeExecuteProjectStatementSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeExecuteProjectStatement, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        department = self.request.user.department
        params["department"] = department
        if all_select_tag:
            handle_list = PhototypeExecuteProjectStatementFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeExecuteProjectStatement.objects.filter(id__in=order_ids, order_status=1)
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
                    data["error"].append("%s未标记单据不可审核" % str(obj.id))
                    n -= 1
                    obj.mistake_tag = 1
                    obj.save()
                    continue

                obj.order_status = 2
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.save()
                logging(obj, user, LogPhototypeExecuteProjectStatement, "确认组项项目")
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
                logging(obj, user, LogPhototypeExecuteProjectStatement, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeExecuteProjectStatement, "预备阶段清除标记")
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
            work_order = PhototypeExecuteProjectStatement.objects.filter(id=id)[0]
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
                photo_order = CPFiles()
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
            logging(work_order, user, LogPhototypeExecuteProjectStatement, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class PhototypeExecuteProjectStatementCheckViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeExecuteProjectStatementSerializer
    filter_class = PhototypeExecuteProjectStatementFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeExecuteProjectStatement.objects.none()
        queryset = PhototypeExecuteProjectStatement.objects.filter(order_status=2).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 2
        f = PhototypeExecuteProjectStatementFilter(params)
        serializer = PhototypeExecuteProjectStatementSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPhototypeExecuteProjectStatement, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 2
        department = self.request.user.department
        params["department"] = department
        if all_select_tag:
            handle_list = PhototypeExecuteProjectStatementFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PhototypeExecuteProjectStatement.objects.filter(id__in=order_ids, order_status=2)
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
                logging(obj, user, LogPhototypeExecuteProjectStatement, "确认组项项目")
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
    def create_total(self, request, *args, **kwargs):
        user = self.request.user
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("系统出错。联系管理员！")
        else:
            obj = PhototypeExecuteProjectStatement.objects.filter(id=id)[0]
        if obj.remaining != obj.settle_amount or int(obj.remaining) <= 0:
            data["false"] = 1
            data["error"].append("已拆分或者结算金额为零的订单不可用全额创建")
            obj.mistake_tag = 2
            obj.save()
            return Response(data)
        _q_payment_all = obj.relationpepstopay_set.all()
        number = len(_q_payment_all) + 1
        _q_payment_check = obj.relationpepstopay_set.all().filter(order_status__in=[1, 2])
        if _q_payment_check.exists():
            data["false"] = 1
            data["error"].append("付款单关联关系错误，请联系管理员")
            obj.mistake_tag = 3
            obj.save()
            return Response(data)
        else:
            payment_order = PaymentOrder()
            payment_order.name = "%s第%s次结算" % (str(obj.code), str(number))
            payment_order.code = "%s-%s" % (str(obj.code), str(number))
            payment_order.supplier = obj.supplier.company
            payment_order.category = 1
            payment_order.pay_amount = obj.settle_amount
            payment_order.creator = user

            try:
                payment_order.save()
                logging(payment_order, user, LogPaymentOrder, "创建")
                obj.remaining -= payment_order.pay_amount
                obj.save()
                logging(obj, user, LogPhototypeExecuteProjectStatement, '完成待分配金额 %s' % str(payment_order.pay_amount))
            except Exception as e:
                data["false"] = 1
                data["error"].append("付款单创建失败：%s", e)
                obj.mistake_tag = 4
                obj.save()
                return Response(data)
        relation_order = RelationPEPSToPay()

        relation_order.origin_obj = obj
        relation_order.origin_amount = obj.settle_amount
        relation_order.pay_amount = payment_order.pay_amount
        relation_order.pay_obj = payment_order
        relation_order.category = 1
        try:
            relation_order.creator = user
            relation_order.save()
            logging(relation_order, user, LogRelationPEPSToPay, "创建")
        except Exception as e:
            data["false"] = 1
            data["error"].append("付款关联关系单创建失败：%s", e)
            obj.mistake_tag = 5
            obj.save()
            return Response(data)

        obj.mistake_tag = 0
        obj.process_tag = 1
        obj.save()
        logging(obj, user, LogPhototypeExecuteProjectStatement, "分配完待结算金额")

        data["successful"] = 1
        return Response(data)

    @action(methods=['patch'], detail=False)
    def create_combine(self, request, *args, **kwargs):
        user = self.request.user
        data = {
            "successful": 0,
            "false": 0,
            "error": []
        }
        id = request.data.get("id", None)
        if not id:
            data["false"] = 1
            data["error"].append("系统出错。联系管理员")

            return response(data)
        else:
            obj = PhototypeExecuteProjectStatement.objects.filter(id=id)[0]
        if obj.remaining != obj.settle_amount and obj.remaining > 0:
            data["false"] = 1
            data["error"].append("已拆分或者结算金额为零的订单不可用全额创建")
            obj.mistake_tag = 2
            obj.save()
            return response(data)

        _q_payment_all = obj.relationpepstopay_set.all()

        if obj.process_tag != 1:
            data["error"].append("%s未标记单据不可确认" % str(obj.id))
            obj.mistake_tag = 1
            obj.save()

            obj.order_status = 2
            obj.mistake_tag = 0
            obj.process_tag = 0
            obj.save()
            logging(obj, user, LogPhototypeExecuteProjectStatement, "确认组项项目")
        else:
            raise serializers.ValidationError("没有可审核的单据！")
        data["successful"] = 1
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
                logging(obj, user, LogPhototypeExecuteProjectStatement, "预备阶段标记确认项目")
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
                logging(obj, user, LogPhototypeExecuteProjectStatement, "预备阶段清除标记")
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
            work_order = PhototypeExecuteProjectStatement.objects.filter(id=id)[0]
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
                photo_order = CPFiles()
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
            logging(work_order, user, LogPhototypeExecuteProjectStatement, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class PhototypeExecuteProjectStatementViewset(viewsets.ModelViewSet):
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
    serializer_class = PhototypeExecuteProjectStatementSerializer
    filter_class = PhototypeExecuteProjectStatementFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PhototypeExecuteProjectStatement.objects.none()
        queryset = PhototypeExecuteProjectStatement.objects.all().order_by("-id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        f = PhototypeExecuteProjectStatementFilter(params)
        serializer = PhototypeExecuteProjectStatementSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = PhototypeExecuteProjectStatement.objects.filter(id=id)[0]
        ret = getlogs(instance, LogPhototypeExecuteProjectStatement)
        return Response(ret)

    @action(methods=['patch'], detail=False)
    def get_file_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = PhototypeExecuteProjectStatement.objects.filter(id=id)[0]
        ret = getfiles(instance, PTFiles)
        return Response(ret)
