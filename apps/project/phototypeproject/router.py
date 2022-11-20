from rest_framework.routers import DefaultRouter
from .views import PhototypeProjectPrepareViewset, PhototypeProjectDevelopViewset, PhototypeProjectViewset, \
    PhototypeProjectDetailsMakeViewset, PhototypeProjectDetailsPurchaseViewset, PhototypeProjectDetailsViewset, PTFilesViewset


phototypeproject_router = DefaultRouter()
phototypeproject_router.register(r'project/phototypeproject/phototypeprojectprepare', PhototypeProjectPrepareViewset, basename='phototypeprojectprepare')
phototypeproject_router.register(r'project/phototypeproject/phototypeprojectdevelop', PhototypeProjectDevelopViewset, basename='phototypeprojectdevelop')
phototypeproject_router.register(r'project/phototypeproject/phototypeproject', PhototypeProjectViewset, basename='phototypeproject')
phototypeproject_router.register(r'project/phototypeproject/phototypeprojectdetailsmake', PhototypeProjectDetailsMakeViewset, basename='phototypeprojectdetailsmake')
phototypeproject_router.register(r'project/phototypeproject/phototypeprojectdetailspurchase', PhototypeProjectDetailsPurchaseViewset, basename='phototypeprojectdetailspurchase')
phototypeproject_router.register(r'project/phototypeproject/phototypeprojectdetails', PhototypeProjectDetailsViewset, basename='phototypeprojectdetails')
phototypeproject_router.register(r'project/phototypeproject/ptfiles', PTFilesViewset, basename='ptfiles')

