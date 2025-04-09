from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    image = models.ImageField(upload_to='users_image', blank=True,
                              null=True)
    

    class Meta:
        db_table = 'user'


    def __str__(self):
        return self.username