from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import UserLoginForm, UserRegistrationForm, \
    ProfileForm
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from orders.models import Order, OrderItem
from .models import User
from django.contrib.auth import login as auth_login

# Create your views here.

def login(request):
    next_page = request.GET.get('next') or reverse('main:product_list')
    
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request, f'Ласкаво просимо, {user.username}!')
            return HttpResponseRedirect(next_page)
        else:
            if not messages.get_messages(request):
                 messages.error(request, 'Не вдалося увійти. Будь ласка, перевірте введені дані та спробуйте знову.')
    else:
        form = UserLoginForm(request=request)

    return render(request, 'users/login.html', {'form': form})


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(
                request, f'{user.username}, ви успішно зареєструвалися! Тепер ви можете увійти.'
            )
            return HttpResponseRedirect(reverse('user:login')) 
    else:
        form = UserRegistrationForm()
    return render(request, 'users/registration.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
        if 'delete_avatar' in request.POST:
            request.user.image.delete(save=True)
            messages.success(request, 'Аватар було видалено.')
            return HttpResponseRedirect(reverse('user:profile'))
        elif form.is_valid():
            form.save()
            messages.success(request, 'Профіль було змінено.')
            return HttpResponseRedirect(reverse('user:profile'))
    else:
        form = ProfileForm(instance=request.user)

    orders = Order.objects.filter(user=request.user).prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.select_related('product'),
        )
    ).order_by('-id')

    return render(request, 'users/profile.html', {'form': form, 'orders': orders})


def logout(request):
    cart_data = request.session.get(settings.CART_SESSION_ID)

    auth.logout(request)

    if cart_data:
        request.session[settings.CART_SESSION_ID] = cart_data
        request.session.modified = True 

    messages.info(request, "Ви вийшли з системи.")
    return redirect(reverse('user:login'))