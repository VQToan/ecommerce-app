from django.urls import reverse
from category.models import Category
from accounts.models import Account
from django.db import models
from store.fields import SecureCharField, SecureEmailField, SecureFloatField, SecureIntegerField, SecureTextField, SecureSlugField

class Product(models.Model):
    product_name = SecureCharField(max_length=200, unique=True)
    slug = SecureSlugField(max_length=200, unique=True)
    description = SecureTextField(max_length=500, blank=True)
    price = SecureIntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = SecureIntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)    # Khi xóa category thì Product bị xóa
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = SecureCharField(max_length=100, choices=variation_category_choice)
    variation_value = SecureCharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = SecureCharField(max_length=100, blank=True)
    review = SecureTextField(max_length=500, blank=True)
    rating = SecureFloatField()
    ip = SecureCharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
