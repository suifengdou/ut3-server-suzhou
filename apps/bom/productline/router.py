from rest_framework.routers import DefaultRouter
from .views import PLCategoryViewset, ProductLineViewset


productline_router = DefaultRouter()
productline_router.register(r'bom/productline/category', PLCategoryViewset, basename='plcategory')
productline_router.register(r'bom/productline/productline', ProductLineViewset, basename='productline')

