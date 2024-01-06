from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from .models import Collection, Order, OrderItem, Product, Review, Cart, CartItem
from .filters import ProductFilter

class ProductViewSet(ModelViewSet):
    
    queryset = Product.objects.select_related('collection').prefetch_related('promotions').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title','id']
    ordering_fields = ['id', 'title', 'price', 'collection__id']
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product__id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product can not be deleted since it is associated with Order Item'},status=405)
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    
    queryset = Collection.objects.annotate(products_count=Count('product')).all()
    serializer_class = CollectionSerializer
    
    def delete(self,request,pk):
        collection = get_object_or_404(Collection,pk=pk)
        if collection.product_set.count() > 0:
            return Response({'error': 'Collection cannot be deleted since it is associated with some Products'}, status=405)
        collection.delete()
        return Response(status=204)

class ReviewViewSet(ModelViewSet):
    
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        return Review.objects.select_related('product').filter(product=self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

class CartViewSet(CreateModelMixin, GenericViewSet, RetrieveModelMixin, DestroyModelMixin):
    
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    
class CartItemViewSet(ModelViewSet):
    
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_queryset(self):
        return CartItem.objects.select_related('cart','product').filter(cart_id=self.kwargs['cart_pk'])
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}