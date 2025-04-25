from django.contrib import admin
from .models import Category, Product, ProductImage

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price',
                    'available', 'created', 'updated',
                    'discount']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available', 'discount']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]