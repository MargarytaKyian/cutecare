from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator

class Pet(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='pets',
                              verbose_name='Власник')
    name = models.CharField(max_length=100, verbose_name='Кличка')
    image = models.ImageField(upload_to='pets_image',
                              blank=True,
                              null=True,
                              verbose_name='Фото улюбленця')
    age_years = models.PositiveIntegerField(null=True, blank=True, verbose_name='Вік (повних років)')
    age_months = models.PositiveIntegerField(null=True, blank=True, verbose_name='Вік (місяців, до 11)')

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Вага (кг)',
        help_text='Вкажіть вагу в кілограмах, наприклад: 5.25',
        validators=[MinValueValidator(0.01)]
    )

    class GenderChoices(models.TextChoices):
        MALE = 'Самець', 'Самець'
        FEMALE = 'Самиця', 'Самиця'
        UNKNOWN = 'Невідомо', 'Невідомо'

    gender = models.CharField(max_length=10, choices=GenderChoices.choices,
                              blank=False, null=True, verbose_name='Стать')

    species = models.CharField(max_length=100, verbose_name='Вид тварини', help_text='Наприклад: Собака, Кіт, Папуга')
    breed = models.CharField(max_length=100, blank=True, null=True, verbose_name='Порода')

    health_features = models.TextField(blank=True, null=True, verbose_name='Особливості здоров\'я та характеру')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата додавання')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата останнього оновлення')

    class Meta:
        verbose_name = 'Улюбленець'
        verbose_name_plural = 'Улюбленці'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.species}) - власник: {self.owner.username}"

    def get_age_display(self):
        parts = []
        if self.age_years is not None:
            if self.age_years == 0 and self.age_months is None:
                 return "Менше року"
            if self.age_years == 1:
                parts.append(f"{self.age_years} рік")
            elif 1 < self.age_years < 5:
                parts.append(f"{self.age_years} роки")
            elif self.age_years >= 5:
                parts.append(f"{self.age_years} років")
            elif self.age_years == 0 and self.age_months is not None:
                 pass


        if self.age_months is not None:
            if self.age_months == 1:
                 parts.append(f"{self.age_months} місяць")
            elif 1 < self.age_months < 5:
                parts.append(f"{self.age_months} місяці")
            elif self.age_months >= 5 or self.age_months == 0:
                parts.append(f"{self.age_months} місяців")
        
        if not parts:
            return "Вік не вказано"
        return " та ".join(parts)
    

    def get_weight_display(self):
        if self.weight is not None:
            normalized_weight = self.weight.normalize()
            if normalized_weight == normalized_weight.to_integral_value():
                return f"{normalized_weight.to_integral_value()} кг"
            return f"{normalized_weight} кг"
        return "Вагу не вказано"