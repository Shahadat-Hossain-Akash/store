from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer, CartSerializer, \
                        CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, \
                        OrderSerializer, OrderItemSerializer, CreateOrderSerializer, UpdateOrderSerializer, ProductImageSerializer
from .models import (Cart, CartItem, Collection, Customer, Order, OrderItem, Product, ProductImage,
    Review)
from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(ModelViewSet):
    
    queryset = Product.objects.select_related('collection',).prefetch_related('promotions', 'images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title','id']
    ordering_fields = ['id', 'title', 'price', 'collection__id']
    permission_classes = [IsAdminOrReadOnly]
    
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product__id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product can not be deleted since it is associated with Order Item'},status=405)
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    
    queryset = Collection.objects.annotate(products_count=Count('product')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    
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
    
    
class CustomerViewSet(ModelViewSet):
    
    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @action(detail=False, methods=('GET','PUT'), permission_classes=[IsAdminOrReadOnly])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        

class OrderItemViewSet(ModelViewSet):
    
    queryset = OrderItem.objects.select_related('product', 'order').all()
    serializer_class = OrderItemSerializer


class OrderViewSet(ModelViewSet):
    
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff:
            return Order.objects.select_related('customer').all()
        customer_id = Customer.objects.get(user_id=user.id)
        return Order.objects.select_related('customer').filter(customer_id=customer_id)
    
class ProductImageViewSet(ModelViewSet):
    
    serializer_class = ProductImageSerializer
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    
    def get_queryset(self):
        return ProductImage.objects.select_related('product').filter(product_id=self.kwargs['product_pk'])