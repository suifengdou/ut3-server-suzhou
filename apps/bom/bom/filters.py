# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from .models import BOM, BOMDetails


class BOMFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = BOM
        fields = "__all__"


class BOMDetailsFilter(django_filters.FilterSet):
    atomic_parts__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = BOMDetails
        fields = "__all__"

