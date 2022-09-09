from rest_framework.routers import DefaultRouter
from .views import ComponentCategoryViewset, ComponentViewset, ComponentVersionViewset


component_router = DefaultRouter()
component_router.register(r'bom/component/componentcategory', ComponentCategoryViewset, basename='componentcategory')
component_router.register(r'bom/component/component', ComponentViewset, basename='component')
component_router.register(r'bom/component/componentversion', ComponentVersionViewset, basename='componentversion')

