# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.urls import reverse
# from .models import Pet
# from .forms import PetForm

# @login_required
# def pet_add(request):
#     if request.method == 'POST':
#         form = PetForm(request.POST, request.FILES)
#         if form.is_valid():
#             pet = form.save(commit=False)
#             pet.owner = request.user
#             pet.save()
#             messages.success(request, f'Улюбленець "{pet.name}" успішно доданий до вашого профілю!')
#             return redirect(reverse('user:profile') + '#pets-section')
#         else:
#             messages.error(request, 'Будь ласка, виправте помилки у формі.')
#     else:
#         form = PetForm()
    
#     context = {
#         'form': form,
#         'action_title': 'Додати нового улюбленця',
#         'submit_button_text': 'Додати улюбленця'
#     }
#     return render(request, 'pets/profile.html', context)

# @login_required
# def pet_edit(request, pet_id):
#     pet = get_object_or_404(Pet, id=pet_id, owner=request.user)

#     if request.method == 'POST':
#         form = PetForm(request.POST, request.FILES, instance=pet)
#         if 'image-clear' in request.POST and pet.image:
#             pet.image.delete(save=False)
#             pet.image = None
        
#         if form.is_valid():
#             form.save()
#             messages.success(request, f'Дані улюбленця "{pet.name}" успішно оновлено!')
#             return redirect(reverse('user:profile') + '#pets-section')
#         else:
#             messages.error(request, 'Будь ласка, виправте помилки у формі.')
#     else:
#         form = PetForm(instance=pet)

#     context = {
#         'form': form,
#         'pet': pet,
#         'action_title': f'Редагувати дані: {pet.name}',
#         'submit_button_text': 'Зберегти зміни'
#     }
#     return render(request, 'pets/profile.html', context)

# @login_required
# def pet_delete(request, pet_id):
#     pet = get_object_or_404(Pet, id=pet_id, owner=request.user)

#     if request.method == 'POST':
#         pet_name = pet.name
#         if pet.image:
#             pet.image.delete(save=False)
#         pet.delete()
#         messages.success(request, f'Улюбленець "{pet_name}" успішно видалений.')
#         return redirect(reverse('user:profile') + '#pets-section')
    
#     context = {'pet': pet}
#     return render(request, 'pets/delete.html', context)