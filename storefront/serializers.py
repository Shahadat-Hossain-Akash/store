import django.db.models.query
from rest_framework import serializers
from storefront.models import Collection, Product, Review, Cart, CartItem

class CollectionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Collection
        fields = ['id','title','products_count']
    
    products_count = serializers.IntegerField(read_only=True)
    
class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'description', 'inventory', 'price','collection']
        

class ReviewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Review
        fields = ['id', 'name', 'description', 'date',]

    def create(self, validated_data):
        
        return Review.objects.create(product_id=self.context['product_id'], **validated_data)
    
class CartItemProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'price']
    
class CartItemSerializer(serializers.ModelSerializer):
    
    product = CartItemProductSerializer()
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self, cart:CartItem):
        return cart.quantity * cart.product.price
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product','quantity', 'total_price']
        
class CartSerializer(serializers.ModelSerializer):
    
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self, cart: CartItem):
        return sum([items.quantity * items.product.price for items in cart.items.all()])
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
        

class AddCartItemSerializer(serializers.ModelSerializer):
    
    product_id = serializers.IntegerField()
    
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Product with the id does not exists!')
        return value
    
    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']
        
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        return self.instance
    
    class Meta:
        model = CartItem
        fields = ['id', 'product_id','quantity']
        
class UpdateCartItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CartItem
        fields = ['quantity']