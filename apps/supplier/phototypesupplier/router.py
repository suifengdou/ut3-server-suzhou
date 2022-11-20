from rest_framework.routers import DefaultRouter
from .views import PhototypeSupplierViewset


phototypesupplier_router = DefaultRouter()
phototypesupplier_router.register(r'supplier/phototypesupplier', PhototypeSupplierViewset, basename='phototypesupplier')

