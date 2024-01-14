from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib import admin
from django.conf import settings
from uuid import uuid4
from storefront.validators import max_image_file_size

class Collection(models.Model):
    title = models.CharField(max_length=255)
    feature_product_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(1)],)
    inventory = models.IntegerField(validators=[MinValueValidator(0)],)
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField("Promotion", blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='storefront/images', validators=[max_image_file_size])
    
    def __str__(self):
        return str(self.image)

class Customer(models.Model):
    class Membership(models.TextChoices):
        BASIC = "BASIC", _("Free plan")
        PREMIUM = "Premium", _("Paid plan")
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(auto_now_add=True, null=True)
    membership = models.CharField(
        choices=Membership, default=Membership.BASIC, max_length=10
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
    @admin.display(ordering='user__username')
    def username(self):
        return self.user.username
    
    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
    
    @admin.display(ordering='user__email')
    def email(self):
        return self.user.email
    
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class Order(models.Model):
    class Status(models.TextChoices):
        P = "P", _("Pending")
        C = "C", _("Completed")
        F = "F", _("Failed")

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(choices=Status, default=Status.P, max_length=1)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        permissions = [
            ("cancel_order", 'Can cancel order')
        ]


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orderitems")
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    placed_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    
    class Meta:
        unique_together = [['cart','product']]


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    

