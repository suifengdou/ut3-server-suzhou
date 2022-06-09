# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import CBOMProject, CBOMProjectDetails


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class CBOMProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = CBOMProject
        fields = "__all__"


class CBOMProjectDetailsFilter(django_filters.FilterSet):
    details__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = CBOMProjectDetails
        fields = "__all__"


