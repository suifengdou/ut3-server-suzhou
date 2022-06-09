from rest_framework.routers import DefaultRouter
from .views import UnitsViewset


department_router = DefaultRouter()
department_router.register(r'bom/material', UnitsViewset, basename='material')

