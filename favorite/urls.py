from django.urls import path
from . import views

app_name = 'favorite'

urlpatterns = [
    path('', views.favorite_list, name='favorite_list'),
    path('add/<int:product_id>/', views.add_to_favorite, name='add_to_favorite'),
    path('remove/<int:product_id>/', views.remove_from_favorite, name='remove_from_favorite'),
]
