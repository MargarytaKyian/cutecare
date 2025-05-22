from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_home_view, name='chat_home'),
    path('new/', views.create_new_chat_view, name='create_new_chat'),
    path('<uuid:session_id>/', views.chat_session_view, name='chat_session'),
    path('api/send_message/<uuid:session_id>/', views.send_message_api_view, name='send_message_api'),
    path('api/delete_session/<uuid:session_id>/', views.delete_chat_session_api_view, name='delete_chat_session_api'),
    path('api/clear_all_sessions/', views.clear_all_sessions_api_view, name='clear_all_sessions_api'),
]