# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import SubUnitProject, SUPFiles


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class SubUnitProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    level__in = NumberInFilter(field_name="level", lookup_expr="in")
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = SubUnitProject
        fields = "__all__"


class SUPFilesFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = SUPFiles
        fields = "__all__"

