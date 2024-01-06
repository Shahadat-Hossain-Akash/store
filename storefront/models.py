from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from uuid import uuid4


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


class Customer(models.Model):
    class Membership(models.TextChoices):
        BASIC = "BASIC", _("Free plan")
        PREMIUM = "Premium", _("Paid plan")

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(auto_now_add=True, null=True)
    membership = models.CharField(
        choices=Membership, default=Membership.BASIC, max_length=10
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Order(models.Model):
    class Status(models.TextChoices):
        P = "P", _("Pending")
        C = "C", _("Completed")
        F = "F", _("Failed")

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(choices=Status, default=Status.P, max_length=1)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)



class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
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