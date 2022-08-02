from rest_framework.routers import DefaultRouter
from .views import MouldSupplierViewset


mouldsup_router = DefaultRouter()
mouldsup_router.register(r'supplier/mouldsup', MouldSupplierViewset, basename='mouldsup')

