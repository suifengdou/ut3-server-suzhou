from rest_framework.routers import DefaultRouter
from .views import PhototypeExecuteProjectStatementSubmitViewset, PhototypeExecuteProjectStatementCheckViewset, PhototypeExecuteProjectStatementViewset


phototypeexecuteprojectstatement_router = DefaultRouter()
phototypeexecuteprojectstatement_router.register(r'statement/phototypeexecuteproject/phototypeexecuteprojectstatementsubmit', PhototypeExecuteProjectStatementSubmitViewset, basename='phototypeexecuteprojectstatementsubmit')
phototypeexecuteprojectstatement_router.register(r'statement/phototypeexecuteproject/phototypeexecuteprojectstatementcheck', PhototypeExecuteProjectStatementCheckViewset, basename='phototypeexecuteprojectstatementcheck')
phototypeexecuteprojectstatement_router.register(r'statement/phototypeexecuteproject/phototypeexecuteprojectstatement', PhototypeExecuteProjectStatementViewset, basename='phototypeexecuteprojectstatement')

