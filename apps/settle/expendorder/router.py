from rest_framework.routers import DefaultRouter
from .views import ExpendOrderSubmitViewset, ExpendOrderCheckViewset, ExpendOrderViewset, ExpendOrderFilesViewset


expendorder_router = DefaultRouter()
expendorder_router.register(r'settle/expend/expendordersubmit', ExpendOrderSubmitViewset, basename='expendordersubmit')
expendorder_router.register(r'settle/expend/expendordercheck', ExpendOrderCheckViewset, basename='expendordercheck')
expendorder_router.register(r'settle/expend/expendorder', ExpendOrderViewset, basename='expendorder')
expendorder_router.register(r'settle/expend/expendorderfiles', ExpendOrderFilesViewset, basename='expendorderfiles')


