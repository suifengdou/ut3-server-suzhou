from rest_framework.routers import DefaultRouter
from .views import OriginUnitProjectSubmitViewset, OriginUnitProjectViewset, UnitProjectConfirmViewset, \
    UnitProjectDevelopViewset, UnitProjectBatchViewset, UnitProjectStopViewset, UnitProjectViewset, \
    OUPPhotoViewset, UPPhotoViewset, UnitProjectSuspendViewset


unitproject_router = DefaultRouter()
unitproject_router.register(r'project/unitproject/originunitprojectsubmit', OriginUnitProjectSubmitViewset, basename='originunitprojectsubmit')
unitproject_router.register(r'project/unitproject/originunitproject', OriginUnitProjectViewset, basename='originunitproject')
unitproject_router.register(r'project/unitproject/unitprojectconfirm', UnitProjectConfirmViewset, basename='unitprojectconfirm')
unitproject_router.register(r'project/unitproject/unitprojectdevelop', UnitProjectDevelopViewset, basename='unitprojectdevelop')
unitproject_router.register(r'project/unitproject/unitprojectbatch', UnitProjectBatchViewset, basename='unitprojectbatch')
unitproject_router.register(r'project/unitproject/unitprojectstop', UnitProjectStopViewset, basename='unitprojectstop')
unitproject_router.register(r'project/unitproject/unitprojectsuspend', UnitProjectSuspendViewset, basename='unitprojectsuspend')
unitproject_router.register(r'project/unitproject/unitproject', UnitProjectViewset, basename='unitproject')
unitproject_router.register(r'project/unitproject/oupphoto', OUPPhotoViewset, basename='oupphoto')
unitproject_router.register(r'project/unitproject/upphoto', UPPhotoViewset, basename='upphoto')

