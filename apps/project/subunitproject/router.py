from rest_framework.routers import DefaultRouter
from .views import SubUnitProjectViewset, SubUnitProjectPrepareViewset, SUPFilesViewset, SubUnitProjectDevelopViewset


subunitproject_router = DefaultRouter()
subunitproject_router.register(r'project/subunitproject/subunitprojectprepare', SubUnitProjectPrepareViewset, basename='subunitprojectprepare')
subunitproject_router.register(r'project/subunitproject/subunitprojectdevelop', SubUnitProjectDevelopViewset, basename='subunitprojectdevelop')
subunitproject_router.register(r'project/subunitproject/subunitproject', SubUnitProjectViewset, basename='subunitproject')
subunitproject_router.register(r'project/subunitproject/supfiles', SUPFilesViewset, basename='supfiles')


