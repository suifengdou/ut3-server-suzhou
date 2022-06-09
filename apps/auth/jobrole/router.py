from rest_framework.routers import DefaultRouter
from .views import JobRoleViewset


jobrole_router = DefaultRouter()
jobrole_router.register(r'auth/jobrole', JobRoleViewset, basename='jobrole')

