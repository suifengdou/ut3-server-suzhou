# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import OriginUnitProject, UnitProject, UnitProjectDetails, ProductLineListProject


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class ProductLineListProjectFilter(django_filters.FilterSet):
    product_line__name = django_filters.CharFilter(lookup_expr='icontains')
    component_category__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = ProductLineListProject
        fields = "__all__"


class OriginUnitProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    level__in = NumberInFilter(field_name="level", lookup_expr="in")
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = OriginUnitProject
        fields = "__all__"


class UnitProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    level__in = NumberInFilter(field_name="level", lookup_expr="in")
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = UnitProject
        fields = "__all__"


class UnitProjectDetailsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = UnitProjectDetails
        fields = "__all__"


