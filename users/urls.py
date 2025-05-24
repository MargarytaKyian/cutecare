from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('logout/', views.logout, name='logout'),
]
