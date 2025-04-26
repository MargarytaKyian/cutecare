from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import UserLoginForm, UserRegistrationForm, \
    ProfileForm
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from orders.models import Order, OrderItem

# Create your views here.

def login(request):
    next_page = request.GET.get('next') or reverse('main:product_list')
    form = UserLoginForm(data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = auth.authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                auth.login(request, user)
                return HttpResponseRedirect(next_page)
            else:
                messages.error(request, 'Invalid login credentials')

    return render(request, 'users/login.html', {'form': form})


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = form.instance
            auth.login(request, user)
            messages.success(
                request, f'{user.username}, Successful Registration'
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
            messages.success(request, 'Avatar has been deleted')
            return HttpResponseRedirect(reverse('user:profile'))
        elif form.is_valid():
            form.save()
            messages.success(request, 'Profile was changed')
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
    auth.logout(request)
    return redirect(reverse('main:product_list'))