from rest_framework.routers import DefaultRouter
from .views import MaterialViewset


material_router = DefaultRouter()
material_router.register(r'bom/material', MaterialViewset, basename='material')

