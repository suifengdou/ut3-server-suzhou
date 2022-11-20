# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import ExpendOrder, ExpendOrderDetails, LogExpendOrder, ExpendOrderFiles


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class ExpendOrderFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = ExpendOrder
        fields = "__all__"


class ExpendOrderDetailsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = ExpendOrderDetails
        fields = "__all__"


class LogExpendOrderFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = LogExpendOrder
        fields = "__all__"


class ExpendOrderFilesFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = ExpendOrderFiles
        fields = "__all__"

