from rest_framework.routers import DefaultRouter
from .views import HandBoardSupplierViewset


handboardsup_router = DefaultRouter()
handboardsup_router.register(r'supplier/handboardsup', HandBoardSupplierViewset, basename='handboardsup')

