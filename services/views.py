from django.shortcuts import render
from .models import Service

def service_list(request):
    services = Service.objects.filter(available=True)
    
    context = {
        'services': services,
    }
    return render(request, 'services/services.html', context)