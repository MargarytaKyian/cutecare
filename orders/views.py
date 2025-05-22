from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart

# Create your views here.


def order_create(request):
    cart = Cart(request)

    has_any_discount_in_cart = any(item['product'].discount > 0 for item in cart if item.get('product'))

    if request.method == 'POST':
        form = OrderCreateForm(request.POST, request=request)
        if form.is_valid():
            order = form.save()
            for item in cart:
                discount_price = item['product'].sell_price
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=discount_price,
                                         quantity=item['quantity'])
            cart.clear()
            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm(request=request)
    return render(request,
                  'order/create.html',
                  {'cart': cart,
                   'form': form,
                   'has_any_discount_in_cart': has_any_discount_in_cart})


@login_required
def order_history(request):
    user_order_list = Order.objects.filter(user=request.user, paid=True).order_by('-created')
    
    orders_per_page = 5
    paginator = Paginator(user_order_list, orders_per_page)
    
    page_number = request.GET.get('page')
    
    try:
        current_page_orders = paginator.page(page_number)
    except PageNotAnInteger:
        current_page_orders = paginator.page(1)
    except EmptyPage:
        current_page_orders = paginator.page(paginator.num_pages)
    
    context = {
        'orders': current_page_orders,
    }
    return render(request, 'order/order_history.html', context)
