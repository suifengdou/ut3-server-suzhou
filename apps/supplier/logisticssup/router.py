from rest_framework.routers import DefaultRouter
from .views import LogisticsSupplierViewset


logistics_router = DefaultRouter()
logistics_router.register(r'supplier/logisticssup', LogisticsSupplierViewset, basename='logisticssup')

