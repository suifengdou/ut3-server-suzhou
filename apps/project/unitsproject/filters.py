# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import OriginUnitProject, UnitProject, OUPPhoto, UPPhoto


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class OriginUnitProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    creator__username = django_filters.CharFilter(lookup_expr='icontains')
    level__in = NumberInFilter(field_name="level", lookup_expr="in")
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = OriginUnitProject
        fields = "__all__"


class UnitProjectFilter(django_filters.FilterSet):
    name__name = django_filters.CharFilter(lookup_expr='icontains')
    name__code = django_filters.CharFilter(lookup_expr='icontains')
    name__number = django_filters.RangeFilter()
    name__units__nationality__name = django_filters.CharFilter(lookup_expr='icontains')
    name__units__unit_number = django_filters.RangeFilter()
    ori_project__name = django_filters.CharFilter(lookup_expr='icontains')
    level__in = NumberInFilter(field_name="level", lookup_expr="in")
    creator__username = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = UnitProject
        fields = "__all__"


class OUPPhotoFilter(django_filters.FilterSet):
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = OUPPhoto
        fields = "__all__"


class UPPhotoFilter(django_filters.FilterSet):
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = UPPhoto
        fields = "__all__"

