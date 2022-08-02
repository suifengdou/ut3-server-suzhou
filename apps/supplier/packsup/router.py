from rest_framework.routers import DefaultRouter
from .views import PackSupplierViewset


packsup_router = DefaultRouter()
packsup_router.register(r'supplier/packsup', PackSupplierViewset, basename='packsup')

