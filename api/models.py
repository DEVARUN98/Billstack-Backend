from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class InventoryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory')
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    item_expiry_date = models.DateField(null=True, blank=True)
    gst = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.item_name} ({self.quantity})"

class Customers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    product_purchased = models.ForeignKey('Products', on_delete=models.CASCADE, related_name='purchases')
    customer_name = models.CharField(max_length=100)
    mob_no = models.CharField(max_length=255, blank=True)
    

    def __str__(self):
        return self.customer_name

class Products(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.product_name
    
class Invoices(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='customers')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='products')
    quantity = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.id} - {self.customer.customer_name}"

class InvoiceNew(models.Model):
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    items = models.JSONField()  # [{"name": "Laptop", "qty": 2, "price": 50000}]
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    gst = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)



