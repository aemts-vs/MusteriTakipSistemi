# notifications/models.py
from django.db import models
from core.models import User # Kime bildirim gönderildiği için
from django.utils import timezone # Zaman damgası için

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('order_status', 'Sipariş Durumu Değişikliği'),
        ('debt_change', 'Borç Durumu Değişikliği'),
        ('stock_alert', 'Stok Uyarısı'),
        ('new_message', 'Yeni Mesaj'),
        ('system_alert', 'Sistem Uyarısı'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="Alıcı")
    message = models.TextField(verbose_name="Bildirim Mesajı")
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES, verbose_name="Bildirim Tipi")
    related_object_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="İlgili Obje ID") # Sipariş ID, Ürün Kodu vb.
    related_object_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="İlgili Obje Tipi") # 'Order', 'Product', 'User'

    is_read = models.BooleanField(default=False, verbose_name="Okundu mu?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Bildirim"
        verbose_name_plural = "Bildirimler"
        ordering = ['-created_at']

    def __str__(self):
        return f"Bildirim ({self.get_notification_type_display()}) - {self.recipient.username}"

    # Ek method: Bildirimi okundu olarak işaretle
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

# --- Bildirim Oluşturma Yardımcı Fonksiyonu ---
def create_notification(recipient, message, notification_type, related_obj=None):
    notification = Notification(
        recipient=recipient,
        message=message,
        notification_type=notification_type
    )
    if related_obj:
        notification.related_object_id = str(related_obj.pk)
        notification.related_object_type = related_obj.__class__.__name__
    notification.save()
    return notification