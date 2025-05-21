from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'requested_datetime', 'status', 'created_at')
    list_filter = ('status', 'service', 'requested_datetime', 'created_at')
    search_fields = ('user__username', 'user__email', 'service__name', 'notes')
    date_hierarchy = 'requested_datetime'
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ("Інформація про запис", {
            'fields': ('user', 'service', 'requested_datetime', 'status', 'notes')
        }),
        ("Системна інформація", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
   
    raw_id_fields = ('user', 'service',)