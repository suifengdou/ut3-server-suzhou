from rest_framework import viewsets, mixins, response
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import CenterSerializer
from .filters import CenterFilter
from .models import Center
from ut3forsuzhou.permissions import Permissions


class CenterViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定中心
    list:
        返回中心列表
    update:
        更新中心信息
    destroy:
        删除中心信息
    create:
        创建中心信息
    partial_update:
        更新部分中心字段
    """
    queryset = Center.objects.all().order_by("id")
    serializer_class = CenterSerializer
    filter_class = CenterFilter
    filter_fields = "__all__"
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['center.view_center']
    }

