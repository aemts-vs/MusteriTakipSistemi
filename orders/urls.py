# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders' # Bu uygulama için bir namespace belirliyoruz

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('add/', views.OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/edit/', views.OrderUpdateView.as_view(), name='order_update'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('<int:pk>/accept/', views.order_accept, name='order_accept'),
    path('<int:pk>/shipped/', views.order_mark_shipped, name='order_mark_shipped'),
    path('<int:pk>/delivered/', views.order_mark_delivered, name='order_mark_delivered'),
    path('<int:pk>/cancelled/', views.order_mark_cancelled, name='order_mark_cancelled'),
    path('<int:pk>/returned/', views.order_mark_returned, name='order_mark_returned'),
    path('<int:pk>/passive/', views.order_mark_passive, name='order_mark_passive'),
]