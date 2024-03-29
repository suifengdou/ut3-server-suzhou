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

from apps.supplier.mouldsup.router import mouldsup_router
from apps.supplier.packsup.router import packsup_router
from apps.supplier.logisticssup.router import logistics_router
from apps.supplier.phototypesupplier.router import phototypesupplier_router

from apps.bom.material.router import material_router
from apps.bom.productline.router import productline_router
from apps.bom.initialparts.router import initialparts_router
from apps.bom.standardlabrary.router import screw_router
from apps.bom.subunit.router import subunit_router
from apps.bom.units.router import units_router
from apps.bom.middleparts.router import middleparts_router
from apps.bom.component.router import component_router
from apps.bom.goods.router import goods_router
from apps.bom.mould.router import mould_router
from apps.bom.bom.router import bom_router
from apps.bom.productcore.router import productcore_router

from apps.utils.geography.router import geography_router

from apps.project.unitproject.router import unitproject_router
from apps.project.subunitproject.router import subunitproject_router
from apps.project.componentproject.router import componentproject_router
from apps.project.initialpartproject.router import initial_parts_project_router
from apps.project.phototypeproject.router import phototypeproject_router
from apps.project.phototypeexecuteproject.router import phototypeexecuteproject_router

from apps.statement.phototypestatement.router import phototypeexecuteprojectstatement_router

from apps.settle.payment.router import paymentorder_router
from apps.settle.expendorder.router import expendorder_router


# 账户权限
route.registry.extend(users_router.registry)
route.registry.extend(jobrole_router.registry)
route.registry.extend(group_router.registry)
# 基本设置
route.registry.extend(center_router.registry)
route.registry.extend(company_router.registry)
route.registry.extend(department_router.registry)
# 供应商
route.registry.extend(mouldsup_router.registry)
route.registry.extend(packsup_router.registry)
route.registry.extend(logistics_router.registry)
route.registry.extend(phototypesupplier_router.registry)
# BOM
route.registry.extend(material_router.registry)
route.registry.extend(productline_router.registry)
route.registry.extend(initialparts_router.registry)
route.registry.extend(screw_router.registry)
route.registry.extend(subunit_router.registry)
route.registry.extend(units_router.registry)
route.registry.extend(middleparts_router.registry)
route.registry.extend(component_router.registry)
route.registry.extend(goods_router.registry)
route.registry.extend(mould_router.registry)
route.registry.extend(bom_router.registry)
route.registry.extend(productcore_router.registry)
# UTILS
route.registry.extend(geography_router.registry)
# PROJECT
route.registry.extend(unitproject_router.registry)
route.registry.extend(subunitproject_router.registry)
route.registry.extend(componentproject_router.registry)
route.registry.extend(initial_parts_project_router.registry)
route.registry.extend(phototypeproject_router.registry)
route.registry.extend(phototypeexecuteproject_router.registry)
# STATEMENT
route.registry.extend(phototypeexecuteprojectstatement_router.registry)
# SETTLE
route.registry.extend(paymentorder_router.registry)
route.registry.extend(expendorder_router.registry)


urlpatterns = [
    url(r'^', include(route.urls)),
    url(r'^api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^api-auth', include("rest_framework.urls")),
    url(r'^docs/', include_docs_urls("UT3接口文档")),
]
