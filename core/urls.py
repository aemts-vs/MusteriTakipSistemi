# core/urls.py
from django.urls import path
from . import views
# Django'nun varsayılan auth_views'lerini de buraya import etmek iyi bir pratiktir,
# PasswordChangeDoneView gibi sınıfları doğrudan kullanırken işe yarar.
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

    # Şifre Sıfırlama URL'leri
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'), # <<<<<< as_as_view() yerine as_view()
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Şifre Değiştirme URL'si (Login gerektirir)
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='core/password_change_done.html'), name='password_change_done'), # <<<<<< BURASI DÜZELTİLDİ

    # Ayarlar ve Personel Yönetimi
    path('settings/profile/', views.ProfileSettingsView.as_view(), name='profile_settings'),
    path('settings/personnel/add/', views.AdminPersonnelManagementView.as_view(), name='admin_add_personnel'),
]