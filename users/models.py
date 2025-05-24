from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    image = models.ImageField(upload_to='users_image', blank=True, null=True,
                              verbose_name='Фото користувача')
    username = models.CharField(max_length=150, blank=True,
                                verbose_name='Нікнейм')
    first_name = models.CharField(max_length=50, blank=True,
                                  verbose_name='Ім\'я')
    last_name = models.CharField(max_length=50, blank=True,
                                 verbose_name='Прізвище'
    )
    middle_name = models.CharField(max_length=50, blank=True, null=True,
                                   verbose_name='По батькові')
    email = models.EmailField(blank=True, verbose_name='Адреса електронної пошти')
    phone_number = models.CharField(max_length=20, blank=True, null=True,
                                    verbose_name='Номер телефону')
    city = models.CharField(max_length=100, blank=True, null=True,
                            verbose_name='Місто')
    address = models.CharField(max_length=250, blank=True, null=True,
                               verbose_name='Адреса') 
    postal_code = models.CharField(max_length=250, blank=True, null=True,
                                   verbose_name='Поштовий індекс') 

    class Meta:
        db_table = 'user'
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

    def __str__(self):
        return self.username