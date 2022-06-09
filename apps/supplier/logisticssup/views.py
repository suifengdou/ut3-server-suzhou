from rest_framework import viewsets, mixins, response
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import LogisticsSupplierSerializer
from .filters import LogisticsSupplierFilter
from .models import LogisticsSupplier
from ut3forsuzhou.permissions import Permissions


class LogisticsSupplierViewset(viewsets.ModelViewSet):
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
    queryset = LogisticsSupplier.objects.all().order_by("id")
    serializer_class = LogisticsSupplierSerializer
    filter_class = LogisticsSupplierFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    # extra_perm_map = {
    #     "GET": ['department.view_department']
    # }

