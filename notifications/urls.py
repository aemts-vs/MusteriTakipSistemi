# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications' # Bu uygulama için bir namespace belirliyoruz

urlpatterns = [
    path('', views.UserNotificationListView.as_view(), name='user_notifications'),
    path('mark-as-read/<int:pk>/', views.MarkNotificationAsReadView.as_view(), name='mark_as_read'),
    path('mark-all-as-read/', views.MarkAllNotificationsAsReadView.as_view(), name='mark_all_as_read'),
    # API endpoint'i için (JS ile dinamik bildirim sayısı almak için)
    # path('unread-count/', views.get_unread_notifications_count, name='unread_count'),
]