from django.contrib import admin
from .models import ChatSession, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('sender', 'text', 'timestamp')
    can_delete = False

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session_id_display', 'sender', 'text_snippet', 'timestamp')
    list_filter = ('sender', 'timestamp', 'session__user')
    search_fields = ('text',)
    readonly_fields = ('timestamp',)

    def session_id_display(self, obj):
        return obj.session.id
    session_id_display.short_description = "ID Сесії"

    def text_snippet(self, obj):
        return obj.text[:75] + '...' if len(obj.text) > 75 else obj.text
    text_snippet.short_description = "Текст"