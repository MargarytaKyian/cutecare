from django.db import models
from django.urls import reverse
from decimal import Decimal
from users.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="Назва")
    slug = models.SlugField(max_length=20, unique=True, verbose_name="URL-Фрагмент (Слаг)")
    image = models.ImageField(upload_to='categories/%Y/%m/%d/',
                              blank=True, null=True,
                              verbose_name="Зображення")
    available = models.BooleanField(default=True, verbose_name="Доступно")

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def get_absolute_url(self):
        return reverse("main:product_list_by_category",
                       args=[self.slug])
    
    def __str__(self):
        return self.name
    

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products',
                                 on_delete=models.CASCADE, verbose_name="Категорія")
    name = models.CharField(max_length=100, verbose_name="Назва")
    slug = models.SlugField(max_length=100, verbose_name="URL-Фрагмент (Слаг)")
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name="Зображення")
    description = models.TextField(blank=True, verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    available = models.BooleanField(default=True, verbose_name="Доступно")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2, verbose_name="Знижка")

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товар'

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
                                on_delete=models.CASCADE, verbose_name="Товар")
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name="Зображення")


    def __str__(self):
        return f'{self.product.name} - {self.image.name}'


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    subject = models.CharField(max_length=100, blank=True, verbose_name="Тема")
    review = models.TextField(max_length=500, blank=True, verbose_name="Відгук")
    rating = models.FloatField(verbose_name="Рейтинг")
    ip = models.CharField(max_length=20, blank=True, verbose_name="IP-Адреса")
    status = models.BooleanField(default=True, verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        verbose_name = 'Відгук та рейтинг'
        verbose_name_plural = 'Відгуки та рейтинги'


    def __str__(self):
        return self.subject
    

@property
def star_list(self):
    full_stars = int(self.rating)
    empty_stars = 5 - full_stars
    return ['full'] * full_stars + ['empty'] * empty_stars
