# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from .models import Units, UnitsVersion, UnitsVersionDetails

class UnitsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Units
        fields = "__all__"


class UnitsVersionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    units__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = UnitsVersion
        fields = "__all__"


class UnitsVersionDetailsFilter(django_filters.FilterSet):
    version__name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    details__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = UnitsVersionDetails
        fields = "__all__"


