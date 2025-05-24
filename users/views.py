from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import UserLoginForm, UserRegistrationForm, \
    ProfileForm
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from orders.models import Order, OrderItem
from pets.models import Pet
from pets.forms import PetForm
from users.models import User
from django.contrib.auth import login as auth_login, update_session_auth_hash

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
    user_instance = request.user

    add_pet_form = PetForm(prefix="add_pet")
    edit_pet_form = PetForm(prefix="edit_pet")
    
    editing_pet_id_on_error = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_pet':
            add_pet_form = PetForm(request.POST, request.FILES, prefix="add_pet")
            if add_pet_form.is_valid():
                pet = add_pet_form.save(commit=False)
                pet.owner = user_instance
                pet.save()
                messages.success(request, f'Улюбленець "{pet.name}" успішно доданий!')
                return HttpResponseRedirect(reverse('user:profile') + '#pets-section')
            else:
                messages.error(request, 'Помилка при додаванні улюбленця. Будь ласка, виправте помилки у формі.')
        
        elif action == 'edit_pet':
            pet_id_to_edit = request.POST.get('pet_id')
            pet_to_edit = get_object_or_404(Pet, id=pet_id_to_edit, owner=user_instance)
            edit_pet_form = PetForm(request.POST, request.FILES, instance=pet_to_edit, prefix="edit_pet")
            editing_pet_id_on_error = pet_id_to_edit
            
            if 'image-clear' in request.POST and pet_to_edit.image:
                 pass

            if edit_pet_form.is_valid():
                edit_pet_form.save()
                messages.success(request, f'Дані улюбленця "{pet_to_edit.name}" успішно оновлено!')
                return HttpResponseRedirect(reverse('user:profile') + '#pets-section')
            else:
                messages.error(request, f'Помилка при редагуванні даних улюбленця "{pet_to_edit.name}". Будь ласка, виправте помилки.')

        elif action == 'delete_pet':
            pet_id_to_delete = request.POST.get('pet_id_for_delete')
            pet_to_delete = get_object_or_404(Pet, id=pet_id_to_delete, owner=user_instance)
            pet_name = pet_to_delete.name
            if pet_to_delete.image:
                pet_to_delete.image.delete(save=False)
            pet_to_delete.delete()
            messages.success(request, f'Улюбленець "{pet_name}" успішно видалений.')
            return HttpResponseRedirect(reverse('user:profile') + '#pets-section')
        

    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=user_instance, files=request.FILES)

        avatar_deleted_message = None
        if request.POST.get('delete_avatar_flag') == 'true':
            if user_instance.image:
                user_instance.image.delete(save=False)
                user_instance.image = None
                avatar_deleted_message = 'Аватар було видалено.'
        
        if form.is_valid():
            form.save()
            user_to_save = form.save(commit=False)
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            password_message = None

            if new_password:
                if new_password == confirm_password:
                    user_to_save.set_password(new_password)
                    password_message = 'Пароль було успішно змінено.'
                else:
                    messages.error(request, 'Паролі не співпадають. Пароль не було змінено.')
                    form.add_error('new_password', 'Паролі не співпадають.') 
            
            user_to_save.save()

            if avatar_deleted_message and not user_to_save.image:
                 messages.success(request, avatar_deleted_message)
            
            if password_message:
                update_session_auth_hash(request, user_to_save)
                messages.success(request, password_message)
            
            if not avatar_deleted_message and not password_message:
                 messages.success(request, 'Профіль було успішно оновлено.')
            elif password_message and not avatar_deleted_message :
                 messages.success(request, 'Профіль було успішно оновлено.')


            return HttpResponseRedirect(reverse('user:profile'))
        else:
            messages.error(request, 'Будь ласка, виправте помилки у формі.')
            
    else:
        form = ProfileForm(instance=user_instance)

    user_pets = Pet.objects.filter(owner=user_instance).order_by('name')

    orders = Order.objects.filter(user=user_instance).prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.select_related('product'),
        )
    ).order_by('-id')

    context = {
        'form': form, 
        'orders': orders,
        'user': user_instance,
        'user_pets': user_pets,
        'add_pet_form': add_pet_form,
        'edit_pet_form': edit_pet_form,
        'editing_pet_id_on_error': editing_pet_id_on_error,
        'add_pet_action_title': 'Додати нового улюбленця',
        'add_pet_submit_button_text': 'Додати улюбленця',
        'edit_pet_action_title': 'Редагувати дані улюбленця',
        'edit_pet_submit_button_text': 'Зберегти зміни',
    }
    return render(request, 'users/profile.html', context)


@login_required
def delete_profile(request):
    if request.method == 'POST':
        user_to_delete = request.user
        user_name = user_to_delete.username

        auth.logout(request)
        user_to_delete.delete()
        
        messages.success(request, f'Профіль "{user_name}" було успішно видалено. Шкода, що Ви йдете.')
        return redirect(reverse('main:product_list'))
    else:
        messages.warning(request, 'Видалення профілю можливе лише через підтвердження у профілі.')
        return redirect(reverse('user:profile'))


def logout(request):
    
    auth.logout(request)

    if settings.CART_SESSION_ID in request.session:
        del request.session[settings.CART_SESSION_ID]
        request.session.modified = True
    
    messages.info(request, "Ви вийшли з системи.")
    return redirect(reverse('user:login'))