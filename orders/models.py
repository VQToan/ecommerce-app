from django.db import models

from accounts.models import Account
from store.models import Product, Variation

from store.fields import SecureCharField, SecureEmailField, SecureFloatField, SecureIntegerField


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = SecureCharField(max_length=100)
    payment_method = SecureCharField(max_length=100)
    amount_paid = SecureCharField(max_length=100)
    status = SecureCharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = SecureCharField(max_length=20)
    first_name = SecureCharField(max_length=50)
    last_name = SecureCharField(max_length=50)
    phone = SecureCharField(max_length=15)
    email = SecureEmailField(max_length=50)
    address_line_1 = SecureCharField(max_length=50)
    address_line_2 = SecureCharField(max_length=50, blank=True)
    country = SecureCharField(max_length=50)
    state = SecureCharField(max_length=50)
    city = SecureCharField(max_length=50)
    order_note = SecureCharField(max_length=100, blank=True)
    order_total = SecureFloatField()
    tax = SecureFloatField()
    status = SecureCharField(max_length=10, choices=STATUS, default='New')
    ip = SecureCharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def full_address(self):
        return "{0} {1}".format(self.address_line_1, self.address_line_2)

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = SecureIntegerField()
    product_price = SecureFloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
