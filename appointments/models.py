from django.db import models
from django.conf import settings
from services.models import Service

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікується підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('cancelled_by_user', 'Скасовано клієнтом'),
        ('cancelled_by_clinic', 'Скасовано клінікою'),
        ('completed', 'Завершено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name="Клієнт"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name="Послуга"
    )
    requested_datetime = models.DateTimeField(verbose_name="Бажана дата та час")
    notes = models.TextField(blank=True, null=True, verbose_name="Примітки клієнта")
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус запису"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення запису")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення запису")

    class Meta:
        verbose_name = "Запис на послугу"
        verbose_name_plural = "Записи на послуги"
        ordering = ['-requested_datetime', '-created_at']

    def __str__(self):
        return f"Запис {self.user.username} на {self.service.name} ({self.requested_datetime.strftime('%d.%m.%Y %H:%M')})"