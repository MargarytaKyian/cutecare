from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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


@require_POST
def remove_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    current_order = order_item.order
    order_id_in_session = request.session.get('order_id')
    
    can_modify = False
    if request.user.is_authenticated and current_order.user == request.user:
        can_modify = True
    elif not current_order.user and current_order.id == order_id_in_session:
        can_modify = True

    if not can_modify:
        messages.error(request, "У вас немає прав для зміни цього замовлення.")
        return redirect(reverse('main:product_list'))

    product_name = order_item.product.name
    order_item.delete()
    
    messages.success(request, f'Товар "{product_name}" було успішно видалено з вашого замовлення.')

    if not current_order.items.exists():
        messages.info(request, "Ваше замовлення тепер порожнє. Можливо, ви захочете його скасувати або додати нові товари.")
    return redirect(reverse('payment:process'))


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
