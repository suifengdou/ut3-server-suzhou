from rest_framework.routers import DefaultRouter
from .views import CenterViewset


department_router = DefaultRouter()
department_router.register(r'base/center', CenterViewset, basename='center')

