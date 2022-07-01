from rest_framework.routers import DefaultRouter
from .views import CenterViewset


center_router = DefaultRouter()
center_router.register(r'base/center', CenterViewset, basename='center')

