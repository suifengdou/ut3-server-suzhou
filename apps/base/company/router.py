from rest_framework.routers import DefaultRouter
from .views import CompanyViewset, ContactsViewset


company_router = DefaultRouter()
company_router.register(r'base/company/company', CompanyViewset, basename='company')
company_router.register(r'base/company/contacts', ContactsViewset, basename='contacts')

