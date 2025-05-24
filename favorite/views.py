from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from main.models import Product
from .models import Favorite
from django.contrib import messages

@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'favorite/favorite_list.html', {'favorites': favorites})

@login_required
def add_to_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f"Товар '{product.name}' додано до збережених.")
    else:
        messages.info(request, f"Товар '{product.name}' уже в збережених.")
    return redirect(request.META.get('HTTP_REFERER', 'main:product_list'))

@login_required
def remove_from_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    deleted_count, _ = Favorite.objects.filter(user=request.user, product=product).delete() 
    
    if deleted_count > 0:
        messages.success(request, f"Товар '{product.name}' видалено із збережених.")
    else:
        messages.info(request, f"Товар '{product.name}' не знайдено у ваших збережених, або вже був видалений.")
        
    return redirect(request.META.get('HTTP_REFERER', 'favorite:favorite_list'))