from rest_framework.routers import DefaultRouter
from .views import ScrewViewset, ScrewSubmitViewset


screw_router = DefaultRouter()
screw_router.register(r'bom/standardlabrary/screw/submit', ScrewSubmitViewset, basename='screwsubmit')
screw_router.register(r'bom/standardlabrary/screw/manage', ScrewViewset, basename='screwmanage')

