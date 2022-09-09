from rest_framework.routers import DefaultRouter
from .views import ProductCoreViewset


productcore_router = DefaultRouter()
productcore_router.register(r'bom/productline/productcore', ProductCoreViewset, basename='productcore')

