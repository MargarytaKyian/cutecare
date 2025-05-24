from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'username',  
        'email',    
        'first_name',
        'last_name',
        'middle_name', 
        'phone_number',
        'is_staff',
        'is_active',
        'date_joined',
    )

    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = BaseUserAdmin.search_fields + ('middle_name', 'phone_number', 'city')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональна інформація', {'fields': (
            'first_name', 
            'last_name', 
            'middle_name', 
            'email'
        )}),
        ('Фото профілю', {'fields': ('image',)}),
        ('Контактна інформація', {'fields': ('phone_number',)}),
        ('Адреса', {'fields': (
            'city', 
            'address', 
            'postal_code'
        )}),
        ('Права доступу', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Дати', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = BaseUserAdmin.readonly_fields + ('date_joined', 'last_login')
    

admin.site.register(User, CustomUserAdmin)