from django.db import models
from django.urls import reverse

from store.fields import SecureCharField, SecureTextField, SecureSlugField


class Category(models.Model):
    category_name = SecureCharField(max_length=50, unique=True)
    slug = SecureSlugField(max_length=100, unique=True)
    description = SecureTextField(max_length=255, blank=True)
    category_image = models.ImageField(upload_to='photos/categories/', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name
