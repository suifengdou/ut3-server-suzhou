# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import CBOM, CBOMVersion, CBOMVersionDetails


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class CBOMFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = CBOM
        fields = "__all__"


class CBOMVersionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = CBOMVersion
        fields = "__all__"


class CBOMVersionDetailsFilter(django_filters.FilterSet):
    atomic_parts__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = CBOMVersionDetails
        fields = "__all__"




