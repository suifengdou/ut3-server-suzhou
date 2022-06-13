# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import MouldExecuteProject, MouldExecuteProjectDetails


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class MouldExecuteProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = MouldExecuteProject
        fields = "__all__"


class MouldExecuteProjectDetailsFilter(django_filters.FilterSet):
    name__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = MouldExecuteProjectDetails
        fields = "__all__"




