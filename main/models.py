from django.db import models
from django.urls import reverse
from decimal import Decimal
from users.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=20, unique=True)
    image = models.ImageField(upload_to='categories/%Y/%m/%d/',
                              blank=True, null=True,
                              verbose_name="Image")
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("main:product_list_by_category",
                       args=[self.slug])
    
    def __str__(self):
        return self.name
    

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:product_detail', args=[self.slug])

    @property
    def sell_price(self):
        if self.discount and self.discount > 0:
            return self.price - (self.price * self.discount / Decimal(100))
        return self.price


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images',
                                on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)


    def __str__(self):
        return f'{self.product.name} - {self.image.name}'


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.subject
    

@property
def star_list(self):
    full_stars = int(self.rating)
    empty_stars = 5 - full_stars
    return ['full'] * full_stars + ['empty'] * empty_stars
