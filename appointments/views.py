from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from .models import Appointment
from .forms import AppointmentForm
from services.models import Service
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def create_appointment(request, service_slug):
    service = get_object_or_404(Service, slug=service_slug, available=True)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            chosen_datetime = form.cleaned_data.get('appointment_datetime')
            if chosen_datetime and chosen_datetime < timezone.now():
                messages.error(request, "Неможливо створити запис на минулий час.")
            else:
                appointment = form.save(commit=False)
                appointment.user = request.user
                appointment.service = service
                appointment.save()
                messages.success(request, f"Ваш запит на послугу «{service.name}» прийнято! Ми зв'яжемося з вами для підтвердження.")
                return redirect('appointments:appointment_history')
    else:
        form = AppointmentForm()

    context = {
        'form': form,
        'service': service,
        'page_title': f"Запис на: {service.name}",
    }
    return render(request, 'appointments/create_appointment.html', context)

@login_required
def appointment_history(request):
    appointments_list = Appointment.objects.filter(user=request.user).select_related('service').order_by('-created_at')

    appointment_per_page = 5
    paginator = Paginator(appointments_list, appointment_per_page)
        
    page_number = request.GET.get('page')
        
    try:
        current_page_appointment = paginator.page(page_number)
    except PageNotAnInteger:
        current_page_appointment = paginator.page(1)
    except EmptyPage:
        current_page_appointment = paginator.page(paginator.num_pages)
    
    context = {
        'appointments': current_page_appointment,
    }
    return render(request, 'appointments/appointment_history.html', context)
