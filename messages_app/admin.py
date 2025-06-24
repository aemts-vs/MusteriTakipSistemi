# messages_app/admin.py
from django.contrib import admin
from .models import Message, MessageReply

class MessageReplyInline(admin.TabularInline):
    model = MessageReply
    extra = 1 # Varsayılan olarak kaç boş yanıt formu göstereceği
    raw_id_fields = ('sender',)
    readonly_fields = ('created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    inlines = [MessageReplyInline] # Mesaj detay sayfasında yanıtları göster

    list_display = ('subject', 'sender', 'message_type', 'order_display', 'status', 'is_read_by_recipient', 'created_at')
    list_filter = ('message_type', 'status', 'is_read_by_recipient', 'created_at')
    search_fields = ('subject', 'content', 'sender__username', 'sender__email', 'order__order_id')
    raw_id_fields = ('sender', 'recipient', 'order')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_replied', 'mark_as_closed']

    def order_display(self, obj):
        return obj.order.order_id if obj.order else "-"
    order_display.short_description = "Sipariş Kodu"

    def mark_as_read(self, request, queryset):
        queryset.update(is_read_by_recipient=True, status='read')
        self.message_user(request, "Seçilen mesajlar okundu olarak işaretlendi.")
    mark_as_read.short_description = "Seçilen mesajları okundu işaretle"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read_by_recipient=False, status='new')
        self.message_user(request, "Seçilen mesajlar okunmadı olarak işaretlendi.")
    mark_as_unread.short_description = "Seçilen mesajları okunmadı işaretle"
    
    def mark_as_replied(self, request, queryset):
        queryset.update(status='replied')
        self.message_user(request, "Seçilen mesajlar cevaplandı olarak işaretlendi.")
    mark_as_replied.short_description = "Seçilen mesajları cevaplandı işaretle"

    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, "Seçilen mesajlar kapalı olarak işaretlendi.")
    mark_as_closed.short_description = "Seçilen mesajları kapalı işaretle"

@admin.register(MessageReply)
class MessageReplyAdmin(admin.ModelAdmin):
    list_display = ('message', 'sender', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('message__subject', 'content', 'sender__username')
    raw_id_fields = ('message', 'sender')