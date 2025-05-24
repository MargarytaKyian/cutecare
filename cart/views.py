from django.shortcuts import render, redirect, \
      get_object_or_404
from django.views.decorators.http import require_POST
from main.models import Product
from .cart import Cart
from .forms import CartAddProductForm

# Create your views here.


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
        
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))


def cart_detail(request):
    cart = Cart(request)
    has_any_discount_in_cart = any(item['product'].discount > 0 for item in cart if item.get('product'))

    return render(request, 'cart/detail.html', 
                  {'cart': cart,
                   'has_any_discount_in_cart': has_any_discount_in_cart})