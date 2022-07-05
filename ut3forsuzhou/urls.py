"""ut3forsuzhou URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import include, path
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

route = DefaultRouter()
from apps.auth.users.router import users_router
from apps.auth.jobrole.router import jobrole_router
from apps.auth.groups.router import group_router
from apps.base.center.router import center_router
from apps.base.company.router import company_router
from apps.base.department.router import department_router
from apps.supplier.handboardsup.router import handboardsup_router

# 账户权限
route.registry.extend(users_router.registry)
route.registry.extend(jobrole_router.registry)
route.registry.extend(group_router.registry)
# 基本设置
route.registry.extend(center_router.registry)
route.registry.extend(company_router.registry)
route.registry.extend(department_router.registry)
# 供应商
route.registry.extend(handboardsup_router.registry)

urlpatterns = [
    url(r'^', include(route.urls)),
    url(r'^api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^api-auth', include("rest_framework.urls")),
    url(r'^docs/', include_docs_urls("UT3接口文档")),
]
