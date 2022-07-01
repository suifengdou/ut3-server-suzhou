# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import CBOMUpdate, CBOMUpdateDetails


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class CBOMUpdateFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = CBOMUpdate
        fields = "__all__"


class CBOMUpdateDetailsFilter(django_filters.FilterSet):
    details__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = CBOMUpdateDetails
        fields = "__all__"

