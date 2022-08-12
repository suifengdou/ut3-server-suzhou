from rest_framework.routers import DefaultRouter
from .views import MouldViewset, MouldVersionViewset, MouldVersionDetailsViewset


mould_router = DefaultRouter()
mould_router.register(r'bom/mould/mould', MouldViewset, basename='mould')
mould_router.register(r'bom/mould/mouldversion', MouldVersionViewset, basename='mouldversion')
mould_router.register(r'bom/mould/mouldversiondetails', MouldVersionDetailsViewset, basename='mouldversiondetails')

