from django.db import models
from main.models import Product
from users.models import User
from django.conf import settings


class Order(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.SET_DEFAULT, blank=True,
                             null=True, default=None, verbose_name="Користувач")
    first_name = models.CharField(max_length=50, verbose_name="Ім'я")
    last_name = models.CharField(max_length=50, verbose_name="Прізвище")
    middle_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="По батькові")
    email = models.EmailField(verbose_name="Електронна пошта")
    phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Номер телефону")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Місто")
    address = models.CharField(max_length=250, blank=True, null=True, verbose_name="Адреса")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Поштовий індекс")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    paid = models.BooleanField(default=False, verbose_name="Оплачено")
    stripe_id = models.CharField(max_length=250, blank=True, verbose_name="ID платежу Stripe")



    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"


    def __str__(self):
        return f'Order {self.id}'
    

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    

    def get_stripe_url(self):
        if not self.stripe_id:
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            path = '/test/'
        else:
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name="Замовлення"
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"


    def __str__(self):
        return str(self.id)
    

    def get_cost(self):
        return self.price * self.quantity