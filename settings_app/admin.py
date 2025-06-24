# settings_app/admin.py
from django.contrib import admin
from .models import UserPreferences

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'navbar_position', 'auto_logout_minutes')
    list_filter = ('theme', 'navbar_position')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',) # Kullanıcı seçimi için arama kutucuğu
    ordering = ('user__username',)