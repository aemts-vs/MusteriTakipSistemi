# settings_app/urls.py
from django.urls import path
from . import views

app_name = 'settings_app' # Bu uygulama için bir namespace belirliyoruz

urlpatterns = [
    path('theme/', views.ThemeSettingsView.as_view(), name='theme_settings'),
    path('navbar-position/change/', views.change_navbar_position, name='change_navbar_position'),
    # Genel sistem ayarları için ayrı bir view ve URL eklenebilir (sadece AdminRequiredMixin ile korunur)
]