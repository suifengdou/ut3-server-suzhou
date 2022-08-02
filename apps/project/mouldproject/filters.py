# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import OriMouldProject, OriMouldProjectDetails, MouldProject, MouldProjectDetails


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class OriMouldProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = OriMouldProject
        fields = "__all__"


class OriMouldProjectDetailsFilter(django_filters.FilterSet):
    details__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = OriMouldProjectDetails
        fields = "__all__"


class MouldProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = MouldProject
        fields = "__all__"


class MouldProjectDetailsFilter(django_filters.FilterSet):
    details__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = MouldProjectDetails
        fields = "__all__"


