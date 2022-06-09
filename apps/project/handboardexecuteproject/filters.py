# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import HandBoardExecuteProject, HandBoardExecuteProjectDetails


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class HandBoardExecuteProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = HandBoardExecuteProject
        fields = "__all__"


class HandBoardExecuteProjectDetailsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = HandBoardExecuteProjectDetails
        fields = "__all__"



