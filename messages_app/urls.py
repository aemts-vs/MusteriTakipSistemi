# messages_app/urls.py
from django.urls import path
from . import views

app_name = 'messages_app' # Bu uygulama için bir namespace belirliyoruz

urlpatterns = [
    path('', views.MessageListView.as_view(), name='message_list'),
    path('send/', views.SendMessageView.as_view(), name='send_message'),
    path('<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('<int:pk>/reply/', views.MessageReplyView.as_view(), name='message_reply'),
]