from django.urls import path
from . import views


app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('remove_item/<int:order_item_id>/', views.remove_order_item, name='remove_order_item'),
    path('history/', views.order_history, name='order_history'),
]
