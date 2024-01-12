from django.urls import path, include
from . import views
from rest_framework_nested import routers



router = routers.DefaultRouter()
router.register('products',viewset=views.ProductViewSet,basename='products')
router.register('collections',viewset=views.CollectionViewSet,basename='collections')
router.register('carts',viewset=views.CartViewSet,basename='carts')
router.register('customers',viewset=views.CustomerViewSet,basename='customers')
router.register('orders',viewset=views.OrderViewSet,basename='orders')

product_router = routers.NestedSimpleRouter(router,'products',lookup='product')
product_router.register('reviews', viewset=views.ReviewViewSet, basename='product-reviews')
cart_router = routers.NestedDefaultRouter(router,'carts',lookup='cart')
cart_router.register('cartitems',viewset=views.CartItemViewSet,basename='cart-cartitems')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(product_router.urls)),
    path(r'', include(cart_router.urls)),
]