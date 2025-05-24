from django.contrib import admin
from .models import Pet

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'species',
                    'gender', 'get_weight_display_admin',
                    'get_age_display', 'created_at')
    list_filter = ('species', 'gender', 'owner', 'created_at')
    search_fields = ('name', 'breed', 'owner__username', 'owner__email')
    raw_id_fields = ('owner',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('owner', 'name', 'image')
        }),
        ('Деталі улюбленця', {
            'fields': ('species', 'gender', 'breed',
                       ('age_years', 'age_months'),
                       'weight', 'health_features')
        }),
        ('Дати', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_age_display(self, obj):
        return obj.get_age_display()
    get_age_display.short_description = 'Вік'

    def get_weight_display_admin(self, obj):
        return obj.get_weight_display()
    get_weight_display_admin.short_description = 'Вага (кг)'