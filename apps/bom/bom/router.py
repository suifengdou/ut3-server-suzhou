from rest_framework.routers import DefaultRouter
from .views import BOMViewset, BOMDetailsViewset


bom_router = DefaultRouter()
bom_router.register(r'bom/bom/bom', BOMViewset, basename='bom')
bom_router.register(r'bom/bom/bomdetails', BOMDetailsViewset, basename='bomdetails')

