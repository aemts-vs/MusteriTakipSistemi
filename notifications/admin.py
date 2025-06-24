# notifications/admin.py
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'message', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'recipient__email', 'message')
    raw_id_fields = ('recipient',) # Alıcı seçimi için arama kutucuğu
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = ['mark_as_read', 'mark_as_unread'] # Toplu işlem butonları

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Seçilen bildirimler okundu olarak işaretlendi.")
    mark_as_read.short_description = "Seçilen bildirimleri okundu olarak işaretle"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, "Seçilen bildirimler okunmadı olarak işaretlendi.")
    mark_as_unread.short_description = "Seçilen bildirimleri okunmadı olarak işaretle"