# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from .models import HandBoard, HandBoardDetails


class HandBoardFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    units__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = HandBoard
        fields = "__all__"


class HandBoardDetailsFilter(django_filters.FilterSet):
    handboard__name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    initial_parts__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = HandBoardDetails
        fields = "__all__"


