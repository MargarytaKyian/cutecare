from django.db import models
from django.conf import settings
import uuid

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Назва чату")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return self.title if self.title else f"Chat with {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Сесія чату"
        verbose_name_plural = "Сесії чатів"

class ChatMessage(models.Model):
    SENDER_USER = 'user'
    SENDER_AI = 'ai'
    SENDER_CHOICES = [
        (SENDER_USER, 'Користувач'),
        (SENDER_AI, 'AI'),
    ]

    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES, verbose_name="Відправник")
    text = models.TextField(verbose_name="Текст повідомлення")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Час відправки")

    def __str__(self):
        return f"{self.get_sender_display()}: {self.text[:50]}..."

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Повідомлення чату"
        verbose_name_plural = "Повідомлення чатів"