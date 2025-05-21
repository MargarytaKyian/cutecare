from django.contrib import admin
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'available', 'created', 'updated')
    list_filter = ('available', 'created', 'updated')
    search_fields = ('name', 'description_short', 'full_description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'available')
        }),
        ('Опис', {
            'fields': ('short_description', 'full_description', 'image')
        }),
        ('Налаштування відображення картки', {
            'classes': ('collapse',),
            'fields': ('icon_class', 'icon_color_class', 'button_text', 'button_icon_class', 'button_color_class')
        }),
        ('Інформація про запис', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created', 'updated')