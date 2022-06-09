from rest_framework.routers import DefaultRouter
from .views import MaterialViewset


department_router = DefaultRouter()
department_router.register(r'bom/material', MaterialViewset, basename='material')

