from rest_framework.routers import DefaultRouter
from .views import HandBoardViewset, HandBoardDetailsViewset


handboard_router = DefaultRouter()
handboard_router.register(r'bom/handboard/handboard', HandBoardViewset, basename='users')
handboard_router.register(r'bom/handboard/handboarddetails', HandBoardDetailsViewset, basename='dashboard')

