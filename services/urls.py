from django.urls import path
from .views import service_list

app_name = 'services'

urlpatterns = [
    path('', service_list, name='service_list'),
]