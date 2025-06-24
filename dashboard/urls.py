# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard' # Bu uygulama için bir namespace belirliyoruz

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='admin_dashboard'),
]