from rest_framework.routers import DefaultRouter
from .views import ComponentProjectViewset, ComponentProjectDevelopViewset, ComponentProjectPrepareViewset, CPFilesViewset


componentproject_router = DefaultRouter()
componentproject_router.register(r'project/componentproject/componentprojectprepare', ComponentProjectPrepareViewset, basename='componentprojectprepare')
componentproject_router.register(r'project/componentproject/componentprojectdevelop', ComponentProjectDevelopViewset, basename='componentprojectdevelop')
componentproject_router.register(r'project/componentproject/componentproject', ComponentProjectViewset, basename='componentproject')
componentproject_router.register(r'project/componentproject/cpfiles', CPFilesViewset, basename='cpfiles')

