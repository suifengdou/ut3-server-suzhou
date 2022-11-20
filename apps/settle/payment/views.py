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
from .models import PaymentOrder, RelationPEPSToPay, LogPaymentOrder, PaymentOrderFiles, LogRelationPEPSToPay
from .serializers import PaymentOrderSerializer, RelationPEPSToPaySerializer, PaymentOrderFilesSerializer
from .filters import PaymentOrderFilter, PaymentOrderFilesFilter, RelationPEPSToPayFilter
from apps.utils.geography.models import City, District
from apps.utils.logging.loggings import logging, getlogs, getfiles
from apps.utils.oss.aliyunoss import AliyunOSS
from apps.statement.phototypestatement.models import LogPhototypeExecuteProjectStatement
from ut3forsuzhou.settings import EXPORT_TOPLIMIT


class PaymentOrderSubmitViewset(viewsets.ModelViewSet):
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
    serializer_class = PaymentOrderSerializer
    filter_class = PaymentOrderFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PaymentOrder.objects.none()
        queryset = PaymentOrder.objects.filter(order_status=1).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 1
        f = PaymentOrderFilter(params)
        serializer = PaymentOrderSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPaymentOrder, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        department = self.request.user.department
        params["department"] = department
        if all_select_tag:
            handle_list = PaymentOrderFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PaymentOrder.objects.filter(id__in=order_ids, order_status=1)
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
                logging(obj, user, LogPaymentOrder, "确认组项项目")
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
                if obj.category == 1:
                    all_phototype_statement = obj.relationpepstopay_set.all().filter(order_status=1)
                    if len(all_phototype_statement) == 0:
                        data["error"].append("%s手板付款单约束单错误，请联系管理员" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                    error_tag = 0
                    for relation_obj in all_phototype_statement:
                        if relation_obj.category == 1:
                            if relation_obj.origin_obj.order_status == 2:
                                relation_obj.origin_obj.remaining += relation_obj.origin_amount
                                relation_obj.origin_obj.save()
                                logging(relation_obj.origin_obj, user, LogPhototypeExecuteProjectStatement, "取消付款单%s, 恢复未结算金额：%s" % (str(obj.name), str(relation_obj.origin_amount)))
                            else:
                                data["error"].append("%s关联结算单状态必须是待审核，其他状态无法驳回" % str(obj.id))
                                n -= 1
                                obj.mistake_tag = 3
                                obj.save()
                                error_tag = 1
                                break
                        elif relation_obj.category == 2:
                            if relation_obj.origin_obj.order_status == 2:
                                relation_obj.origin_obj.remaining += relation_obj.pay_amount
                                relation_obj.origin_obj.save()
                                logging(relation_obj.origin_obj, user, LogPhototypeExecuteProjectStatement, "取消付款单%s, 恢复未结算金额：%s" % (str(obj.name), str(relation_obj.pay_amount)))
                            else:
                                data["error"].append("%s关联结算单状态必须是待审核，其他状态无法驳回" % str(obj.id))
                                n -= 1
                                obj.mistake_tag = 3
                                obj.save()
                                error_tag = 1
                                break
                        else:
                            data["error"].append("%s手板付款单约束单错误，请联系管理员" % str(obj.id))
                            n -= 1
                            obj.mistake_tag = 2
                            obj.save()
                            break
                        relation_obj.origin_amount = 0
                        relation_obj.pay_amount = 0
                        relation_obj.order_status = 0
                        relation_obj.save()
                        logging(relation_obj, user, LogRelationPEPSToPay, "取消手板付款单约束单")
                    if error_tag:
                        continue
                elif obj.category == 2:
                    pass
                elif obj.category == 3:
                    pass
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.oa_id = None
                obj.order_status = 0
                obj.save()
                logging(obj, user, LogPaymentOrder, "取消付款单")
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
                logging(obj, user, LogPaymentOrder, "预备阶段标记确认项目")
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
                logging(obj, user, LogPaymentOrder, "预备阶段清除标记")
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
            work_order = PaymentOrder.objects.filter(id=id)[0]
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
                photo_order = PaymentOrderFiles()
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
            logging(work_order, user, LogPaymentOrder, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class PaymentOrderCheckViewset(viewsets.ModelViewSet):
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
    serializer_class = PaymentOrderSerializer
    filter_class = PaymentOrderFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PaymentOrder.objects.none()
        queryset = PaymentOrder.objects.filter(order_status=1).order_by("id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        params["order_status"] = 1
        f = PaymentOrderFilter(params)
        serializer = PaymentOrderSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        for obj in serializer.instance:
            logging(obj, user, LogPaymentOrder, "导出")
        return Response(serializer.data)

    def get_handle_list(self, params):
        params.pop("page", None)
        all_select_tag = params.pop("allSelectTag", None)
        params["order_status"] = 1
        department = self.request.user.department
        params["department"] = department
        if all_select_tag:
            handle_list = PaymentOrderFilter(params).qs
        else:
            order_ids = params.pop("ids", None)
            if order_ids:
                handle_list = PaymentOrder.objects.filter(id__in=order_ids, order_status=1)
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
                pass
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
                if obj.category == 1:
                    all_phototype_statement = obj.relationpepstopay_set.all().filter(order_status=1)
                    if len(all_phototype_statement) == 0:
                        data["error"].append("%s手板付款单约束单错误，请联系管理员" % str(obj.id))
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                    error_tag = 0
                    for relation_obj in all_phototype_statement:
                        if relation_obj.category == 1:
                            if relation_obj.origin_obj.order_status == 2:
                                relation_obj.origin_obj.remaining += relation_obj.origin_amount
                                relation_obj.origin_obj.save()
                                logging(relation_obj.origin_obj, user, LogPhototypeExecuteProjectStatement, "取消付款单%s, 恢复未结算金额：%s" % (str(obj.name), str(relation_obj.origin_amount)))
                            else:
                                data["error"].append("%s关联结算单状态必须是待审核，其他状态无法驳回" % str(obj.id))
                                n -= 1
                                obj.mistake_tag = 3
                                obj.save()
                                error_tag = 1
                                break
                        elif relation_obj.category == 2:
                            if relation_obj.origin_obj.order_status == 2:
                                relation_obj.origin_obj.remaining += relation_obj.pay_amount
                                relation_obj.origin_obj.save()
                                logging(relation_obj.origin_obj, user, LogPhototypeExecuteProjectStatement, "取消付款单%s, 恢复未结算金额：%s" % (str(obj.name), str(relation_obj.pay_amount)))
                            else:
                                data["error"].append("%s关联结算单状态必须是待审核，其他状态无法驳回" % str(obj.id))
                                n -= 1
                                obj.mistake_tag = 3
                                obj.save()
                                error_tag = 1
                                break
                        else:
                            data["error"].append("%s手板付款单约束单错误，请联系管理员" % str(obj.id))
                            n -= 1
                            obj.mistake_tag = 2
                            obj.save()
                            break
                        relation_obj.origin_amount = 0
                        relation_obj.pay_amount = 0
                        relation_obj.order_status = 0
                        relation_obj.save()
                        logging(relation_obj, user, LogRelationPEPSToPay, "取消手板付款单约束单")
                    if error_tag:
                        continue
                elif obj.category == 2:
                    pass
                elif obj.category == 3:
                    pass
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.order_status = 0
                obj.save()
                logging(obj, user, LogPaymentOrder, "取消付款单")
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
                logging(obj, user, LogPaymentOrder, "预备阶段标记确认项目")
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
                logging(obj, user, LogPaymentOrder, "预备阶段清除标记")
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
            work_order = PaymentOrder.objects.filter(id=id)[0]
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
                photo_order = PaymentOrderFiles()
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
            logging(work_order, user, LogPaymentOrder, "上传：%s" % str(log_file_names))
        else:
            data = {
                "error": "上传文件未找到！"
            }
        return Response(data)


class PaymentOrderViewset(viewsets.ModelViewSet):
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
    serializer_class = PaymentOrderSerializer
    filter_class = PaymentOrderFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PaymentOrder.objects.none()
        queryset = PaymentOrder.objects.all().order_by("-id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        f = PaymentOrderFilter(params)
        serializer = PaymentOrderSerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = PaymentOrder.objects.filter(id=id)[0]
        ret = getlogs(instance, LogPaymentOrder)
        return Response(ret)

    @action(methods=['patch'], detail=False)
    def get_file_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = PaymentOrder.objects.filter(id=id)[0]
        ret = getfiles(instance, PaymentOrderFiles)
        return Response(ret)


# 手板结算单对应支付单约束
class RelationPEPSToPayViewset(viewsets.ModelViewSet):
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
    serializer_class = RelationPEPSToPaySerializer
    filter_class = RelationPEPSToPayFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return RelationPEPSToPay.objects.none()
        queryset = RelationPEPSToPay.objects.all().order_by("-id")
        return queryset

    @action(methods=['patch'], detail=False)
    def export(self, request, *args, **kwargs):
        user = self.request.user
        request.data.pop("page", None)
        request.data.pop("allSelectTag", None)
        params = request.data
        f = RelationPEPSToPayFilter(params)
        serializer = RelationPEPSToPaySerializer(f.qs[:EXPORT_TOPLIMIT], many=True)
        return Response(serializer.data)

    @action(methods=['patch'], detail=False)
    def get_log_details(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        if not id:
            raise serializers.ValidationError("未找到单据！")
        instance = RelationPEPSToPay.objects.filter(id=id)[0]
        ret = getlogs(instance, LogRelationPEPSToPay)
        return Response(ret)


class PaymentOrderFilesViewset(viewsets.ModelViewSet):
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
    serializer_class = PaymentOrderFilesSerializer
    filter_class = PaymentOrderFilesFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['manualorder.view_manualorder']
    }

    def get_queryset(self):
        if not self.request:
            return PaymentOrderFiles.objects.none()
        queryset = PaymentOrderFiles.objects.all().order_by("id")
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
            photo_order = PaymentOrderFiles.objects.filter(id=id, creator=user, is_delete=False)
            if photo_order.exists():
                photo_order = photo_order[0]
                photo_order.is_delete = 1
                photo_order.save()
                data["successful"] += 1
                logging(photo_order.workorder, user, LogPaymentOrder, "删除文档：%s" % photo_order.name)
            else:
                data["false"] += 1
                data["error"].append("只有创建者才有删除权限")
        else:
            data["false"] += 1
            data["error"].append("没有找到删除对象")
        return Response(data)


