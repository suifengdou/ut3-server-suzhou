import pandas as pd
from django.shortcuts import render
from rest_framework import viewsets, mixins, response
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import JobRoleSerializer
from .filters import JobRoleFilter
from ut3forsuzhou.permissions import Permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import JobRole


class JobRoleViewset(viewsets.ModelViewSet):
    """
    retrieve:
        返回指定用户
    list:
        返回用户列表
    update:
        更新用户信息
    destroy:
        删除用户信息
    create:
        创建用户信息
    partial_update:
        更新部分用户字段
    """
    queryset = JobRole.objects.all().order_by("id")
    serializer_class = JobRoleSerializer
    filter_class = JobRoleFilter
    filter_fields = ("username", "creator", "created_time", "is_staff", "is_active")
    permission_classes = (IsAuthenticated, Permissions)
    extra_perm_map = {
        "GET": ['jobrole.view_jobrole']
    }

    def list(self, request, *args, **kwargs):
        return super(JobRoleViewset, self).list(request, *args, **kwargs)

