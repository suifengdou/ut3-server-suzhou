from rest_framework.routers import DefaultRouter
from .views import MiddlePartsViewset, MiddlePartsVersionViewset


middleparts_router = DefaultRouter()
middleparts_router.register(r'bom/middleparts/middleparts', MiddlePartsViewset, basename='middleparts')
middleparts_router.register(r'bom/middleparts/middlepartsversion', MiddlePartsVersionViewset, basename='middlepartsversion')

