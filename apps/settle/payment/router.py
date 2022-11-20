from rest_framework.routers import DefaultRouter
from .views import PaymentOrderSubmitViewset, PaymentOrderCheckViewset, PaymentOrderViewset, PaymentOrderFilesViewset, \
    RelationPEPSToPayViewset


paymentorder_router = DefaultRouter()
paymentorder_router.register(r'settle/payment/paymentordersubmit', PaymentOrderSubmitViewset, basename='paymentordersubmit')
paymentorder_router.register(r'settle/payment/paymentordercheck', PaymentOrderCheckViewset, basename='paymentordercheck')
paymentorder_router.register(r'settle/payment/paymentorder', PaymentOrderViewset, basename='paymentorder')
paymentorder_router.register(r'settle/payment/paymentorderfiles', PaymentOrderFilesViewset, basename='paymentorderfiles')
paymentorder_router.register(r'settle/payment/relationpepstopay', RelationPEPSToPayViewset, basename='relationpepstopay')


