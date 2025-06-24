# messages_app/models.py
from django.db import models
from core.models import User # Mesajı gönderen ve alıcı için User modeli
from orders.models import Order # Mesajın hangi siparişe ait olduğu için

class Message(models.Model):
    MESSAGE_TYPE_CHOICES = (
        ('complaint', 'Şikayet'),
        ('request', 'Talep'),
        ('general', 'Genel'),
        ('support', 'Destek'),
    )
    MESSAGE_STATUS_CHOICES = (
        ('new', 'Yeni'),
        ('read', 'Okundu'),
        ('replied', 'Cevaplandı'),
        ('closed', 'Kapalı'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Gönderen")
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_messages', verbose_name="Alıcı") # Personel/Yönetici olabilir
    subject = models.CharField(max_length=255, verbose_name="Konu")
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='general', verbose_name="Mesaj Tipi")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="İlgili Sipariş")
    content = models.TextField(verbose_name="Mesaj İçeriği")
    status = models.CharField(max_length=20, choices=MESSAGE_STATUS_CHOICES, default='new', verbose_name="Durum")
    is_read_by_recipient = models.BooleanField(default=False, verbose_name="Alıcı Tarafından Okundu mu?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderim Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Mesaj"
        verbose_name_plural = "Mesajlar"
        ordering = ['-created_at'] # En yeni mesajlar üstte

    def __str__(self):
        return f"Mesaj: {self.subject} (Gönderen: {self.sender.username})"

    def mark_as_read(self):
        if not self.is_read_by_recipient:
            self.is_read_by_recipient = True
            self.status = 'read'
            self.save()

class MessageReply(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='replies', verbose_name="Mesaj")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Gönderen")
    content = models.TextField(verbose_name="Yanıt İçeriği")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yanıt Tarihi")

    class Meta:
        verbose_name = "Mesaj Yanıtı"
        verbose_name_plural = "Mesaj Yanıtları"
        ordering = ['created_at']

    def __str__(self):
        return f"Yanıt: {self.message.subject} ({self.sender.username})"