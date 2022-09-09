import datetime
import hashlib
from rest_framework import viewsets, mixins, response
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UnitsSerializer, UnitsVersionSerializer
from .filters import UnitsFilter, UnitsVersionFilter
from .models import Units, UnitsVersion
from ut3forsuzhou.permissions import Permissions
import oss2
from rest_framework.decorators import action
from rest_framework.response import Response
from ut3forsuzhou.settings import OSS_CONFIG
from itertools import islice
from apps.utils.oss.aliyunoss import AliyunOSS


class UnitsViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定公司
    list:
        返回公司列表
    update:
        更新公司信息
    destroy:
        删除公司信息
    create:
        创建公司信息
    partial_update:
        更新部分公司字段
    """
    queryset = Units.objects.all().order_by("id")
    serializer_class = UnitsSerializer
    filter_class = UnitsFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['company.view_company']
    }


class UnitsVersionViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定公司
    list:
        返回公司列表
    update:
        更新公司信息
    destroy:
        删除公司信息
    create:
        创建公司信息
    partial_update:
        更新部分公司字段
    """
    queryset = UnitsVersion.objects.all().order_by("id")
    serializer_class = UnitsVersionSerializer
    filter_class = UnitsVersionFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['company.view_company']
    }

