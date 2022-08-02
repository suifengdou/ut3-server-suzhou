from rest_framework.routers import DefaultRouter
from .views import SubUnitViewset, SubUnitVersionViewset


subunit_router = DefaultRouter()
subunit_router.register(r'bom/subunit/subunit', SubUnitViewset, basename='subunit')
subunit_router.register(r'bom/subunit/subnunitversion', SubUnitVersionViewset, basename='subnunitversion')

