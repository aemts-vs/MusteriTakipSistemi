# customers/urls.py
from django.urls import path
from . import views

app_name = 'customers' # Bu uygulama için bir namespace belirliyoruz

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customer_list'),
    path('<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    path('<int:pk>/deactivate/', views.customer_deactivate, name='customer_deactivate'),
    path('<int:pk>/activate/', views.customer_activate, name='customer_activate'),
]