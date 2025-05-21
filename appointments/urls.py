from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('new/<slug:service_slug>/', views.create_appointment, name='create_appointment'),
    path('history/', views.appointment_history, name='appointment_history'),
]