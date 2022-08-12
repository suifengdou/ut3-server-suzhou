from rest_framework.routers import DefaultRouter
from .views import UnitsViewset, UnitsVersionViewset, UnitsVersionDetailsViewset


units_router = DefaultRouter()
units_router.register(r'bom/units/units', UnitsViewset, basename='units')
units_router.register(r'bom/units/unitsversion', UnitsVersionViewset, basename='unitsversion')
units_router.register(r'bom/units/unitsversiondetails', UnitsVersionDetailsViewset, basename='unitsversiondetails')

