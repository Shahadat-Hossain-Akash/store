import django.db
from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from django.db.models import Count, Q
from django.utils.html import format_html, urlencode
from .models import Collection,Product,Customer,Order,OrderItem,ProductImage



@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','product_count']
    search_fields = ['title']
    show_full_result_count  =False
    
    @admin.display(ordering="product_count")
    def product_count(self, collection):
        url = (reverse('admin:storefront_product_changelist')+'?'+ urlencode({'collection__id': str(collection.id)}))
        return format_html('<a href={}>{}</a>', url, collection.product_count)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(product_count=Count('product'))
    
class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'
    MEDIUM_RANGE = '>10 and <90'
    high = '>=90'
    
    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [("<10", 'low'),(self.MEDIUM_RANGE, 'medium'),(self.high, 'high'),]
    
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        elif self.value() == self.MEDIUM_RANGE:
            return queryset.filter(Q(inventory__gte=10) & Q(inventory__lt=90))
        elif self.value() == self.high:
            return queryset.filter(Q(inventory__gte=90))

class ProductImageInline(admin.TabularInline):
    readonly_fields = ['thumbnail']
    model = ProductImage
    
    def thumbnail(self, instance):
        if instance.image.name != '':
            return mark_safe(f'<img src="{instance.image.url}" alt="" style="width:50px; height:50px; object-fit:cover;"/>')

class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields=['collection']
    prepopulated_fields = {
        "slug": ["title"]
    }
    actions = ['clear_inventory']
    inlines = [ProductImageInline]
    list_display=['title', 'price', 'collection', 'inventory_status']
    list_select_related=['collection']
    list_per_page = 20
    list_editable = ['price']
    list_select_related = ['collection']
    list_filter = [InventoryFilter]
    search_fields=['title']
    show_full_result_count = False
    
    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        
        if product.inventory == 0:
            return "Out of stock"
        elif product.inventory <= 10 :
            return "Running low on Stock"
        elif product.inventory > 10 and product.inventory <=90:
            return "Adequate"
        else:
            return "In stock"
    
    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        updated_inventory = queryset.update(inventory=0)
        self.message_user(request, f"{updated_inventory} products were successfully updated",)
    
class CustomerAdmin(admin.ModelAdmin):
    list_display=['username', 'first_name', 'last_name', 'membership', 'email', 'orders']
    list_per_page = 20
    list_editable = ['membership']
    list_select_related = ['user']
    search_fields = ['first_name__startswith', 'last_name__startswith', 'email']
    ordering = ['user__first_name', 'user__last_name']
    show_full_result_count = False
    autocomplete_fields = ['user']
    
    @admin.display(ordering="orders_count")
    def orders(self, customer):
        url = (reverse('admin:storefront_order_changelist')+'?'+ urlencode({'customer__id': str(customer.id)}))
        return format_html('<a href={}>{}</a>', url, customer.orders_count)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(orders_count=Count('order'))

class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    model = OrderItem
    
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ["customer", 'payment_status', 'placed_at']
    list_select_related = ['customer']
    list_per_page = 20
    list_editable = ['payment_status']
    show_full_result_count = False
    

# admin.site.register(Collection)
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
