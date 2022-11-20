from rest_framework.routers import DefaultRouter
from .views import OriInitialPartProjectSubmitViewset, OriInitialPartProjectViewset, InitialPartProjectConfirmViewset, \
    InitialPartProjectViewset, OIPPFilesViewset, IPPFilesViewset


initial_parts_project_router = DefaultRouter()
initial_parts_project_router.register(r'project/initpartproject/oriinitpartprojectsubmit', OriInitialPartProjectSubmitViewset, basename='oriinitpartprojectsubmit')
initial_parts_project_router.register(r'project/initpartproject/oriinitpartproject', OriInitialPartProjectViewset, basename='oriinitpartproject')
initial_parts_project_router.register(r'project/initpartproject/initpartprojectconfirm', InitialPartProjectConfirmViewset, basename='initpartprojectconfirm')
initial_parts_project_router.register(r'project/initpartproject/initpartproject', InitialPartProjectViewset, basename='initpartproject')
initial_parts_project_router.register(r'project/initpartproject/oippfiles', OIPPFilesViewset, basename='oippfiles')
initial_parts_project_router.register(r'project/initpartproject/ippfiles', IPPFilesViewset, basename='ippfiles')

