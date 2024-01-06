from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.urls import reverse

from django.db.models import Count, Q
from django.utils.html import format_html, urlencode
from .models import Collection,Product,Customer,Order,OrderItem



@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','product_count']
    search_fields = ['title']
    
    @admin.display(ordering="product_count")
    def product_count(self, collection):
        url = (reverse('admin:storefront_product_changelist')+'?'+ urlencode({'collection__id': str(collection.id)}))
        return format_html('<a href={}>{}</a>', url, collection.product_count)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(product_count=Count('product'))
    
class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'
    medium = '>10 and <90'
    high = '>=90'
    
    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [("<10", 'low'),('>10 and <90', 'medium'),('>=90', 'high'),]
    
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        elif self.value() == '>10 and <90':
            return queryset.filter(Q(inventory__gte=10) & Q(inventory__lt=90))
        elif self.value() == '>=90':
            return queryset.filter(Q(inventory__gte=90))

class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields=['collection']
    prepopulated_fields = {
        "slug": ["title"]
    }
    actions = ['clear_inventory']
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
    list_display=['first_name', 'last_name', 'membership', 'email']
    list_per_page = 20
    list_editable = ['membership']
    search_fields = ['first_name__startswith', 'last_name__startswith']
    show_full_result_count = False
    
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
