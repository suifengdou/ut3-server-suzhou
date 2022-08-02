from rest_framework.routers import DefaultRouter
from .views import PartsCategorySerializerViewset, InitialPartsSerializerViewset


initialparts_router = DefaultRouter()
initialparts_router.register(r'bom/initialparts/partscategory', PartsCategorySerializerViewset, basename='partscategory')
initialparts_router.register(r'bom/initialparts/initialparts', InitialPartsSerializerViewset, basename='initialparts')

