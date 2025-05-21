from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва послуги")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL-фрагмент (слаг)")
    short_description = models.CharField(max_length=255, verbose_name="Короткий опис")
    full_description = models.TextField(verbose_name="Повний опис (для деталей)")
    image = models.ImageField(upload_to='services_images/', blank=True, null=True, verbose_name="Зображення")
    
    # Поля для кастомізації картки послуги в шаблоні
    icon_class = models.CharField(max_length=100, default="fas fa-clinic-medical", verbose_name="Клас іконки Font Awesome (напр., fas fa-paw)")
    icon_color_class = models.CharField(max_length=50, default="text-indigo-500", verbose_name="Клас кольору іконки (напр., text-pink-500)")
    button_text = models.CharField(max_length=50, default="Записатися", verbose_name="Текст кнопки")
    button_icon_class = models.CharField(max_length=50, default="fas fa-calendar-check", verbose_name="Клас іконки для кнопки (напр., fas fa-cut)")
    button_color_class = models.CharField(max_length=100, default="bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500", verbose_name="CSS класи для кольору кнопки")

    available = models.BooleanField(default=True, verbose_name="Доступно")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)