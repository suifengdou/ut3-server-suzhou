from rest_framework.routers import DefaultRouter
from .views import AtomicPartsViewset, AtomicPartsVersionViewset, GoodsViewset, GoodsDetailsViewset


goods_router = DefaultRouter()
goods_router.register(r'bom/goods/atomicparts', AtomicPartsViewset, basename='atomicparts')
goods_router.register(r'bom/goods/atomicpartsversion', AtomicPartsVersionViewset, basename='atomicpartsversion')
goods_router.register(r'bom/goods/goods', GoodsViewset, basename='goods')
goods_router.register(r'bom/goods/goodsdetails', GoodsDetailsViewset, basename='goodsdetails')

