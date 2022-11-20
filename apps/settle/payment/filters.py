# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:27
# @Author  : Hann
# @Site    : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from .models import PaymentOrder, RelationPEPSToPay, PaymentOrderFiles


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class PaymentOrderFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = PaymentOrder
        fields = "__all__"


class PaymentOrderFilesFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = PaymentOrderFiles
        fields = "__all__"



class RelationPEPSToPayFilter(django_filters.FilterSet):
    origin_obj__name = django_filters.CharFilter(lookup_expr='icontains')
    pay_obj__name = django_filters.CharFilter(lookup_expr='icontains')
    created_time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = RelationPEPSToPay
        fields = "__all__"
