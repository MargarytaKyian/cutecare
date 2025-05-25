from django.db import models
from django.conf import settings
from main.models import Product

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='favorites', verbose_name="Користувач")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='favorited_by', verbose_name="Товар")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']
        verbose_name = 'Збережене'
        verbose_name_plural = 'Збережені'


    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"
