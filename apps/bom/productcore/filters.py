# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from .models import ProductCore


class ProductCoreFilter(django_filters.FilterSet):
    product_line__name = django_filters.CharFilter(lookup_expr='icontains')
    component_category__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = ProductCore
        fields = "__all__"



