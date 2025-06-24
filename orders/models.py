# orders/models.py
import uuid
from django.db import models
from core.models import User # Müşterilerimiz core.User modelinden geliyor
from stock.models import Product # Sipariş kalemleri için Product modelinden
from decimal import Decimal # DecimalField için

class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('new', 'Yeni Sipariş'),
        ('accepted', 'Kabul Edildi / Hazırlanıyor'),
        ('shipped', 'Kargoya Verildi'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal Edildi'),
        ('returned', 'İade Edildi'),
        ('passive', 'Pasif'), # Sipariş silinmesin pasife alınsın diye ekledik
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Ödeme Bekleniyor'),
        ('paid', 'Ödendi'),
        ('refunded', 'İade Edildi'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Kredi Kartı'),
        ('bank_transfer', 'Havale/EFT'),
        ('cash_on_delivery', 'Kapıda Ödeme'),
        ('installment', 'Vadeli Ödeme'),
    )

    order_id = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Sipariş Numarası/ID")
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_orders', verbose_name="Müşteri")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Sipariş Tarihi ve Saati")
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='new', verbose_name="Sipariş Durumu")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Toplam Ödeme Tutarı")
    is_completed = models.BooleanField(default=False, verbose_name="Sipariş Tamamlandı mı?")

    # Ödeme Bilgileri
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="Ödeme Durumu")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True, verbose_name="Ödeme Yöntemi")

    # Teslimat/Kargo Bilgileri
    delivery_address = models.TextField(verbose_name="Teslimat Adresi")
    shipping_company = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kargo Firması")
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Takip Numarası")
    estimated_delivery_date = models.DateField(blank=True, null=True, verbose_name="Tahmini Teslimat Tarihi")

    # İndirim/Promosyon Bilgileri
    discount_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="İndirim/Promosyon Kodu")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="İndirim Tutarı")

    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"
        ordering = ['-order_date']

    def __str__(self):
        return f"Sipariş {self.order_id} - {self.customer.get_full_name() if self.customer else 'Misafir'}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = str(uuid.uuid4()).upper()[:8] # Benzersiz, kısa bir sipariş ID'si
        super().save(*args, **kwargs)

    @property
    def get_total_items_price(self):
        # Toplam ürün fiyatını OrderItem'lardan hesaplar.
        # Eğer henüz kaydedilmemiş veya item'lar çekilmemişse 0 döner.
        # İlişkili OrderItem'lar zaten getirilmiş olacağı için query yapmaya gerek yok.
        return sum(item.total_price for item in self.items.all()) if self.pk else Decimal('0.00')

    # Bu metod views.py'den çağrılacak
    def update_total_amount(self):
        # Siparişin toplam tutarını hesaplar (ürünler - indirim)
        self.total_amount = self.get_total_items_price - self.discount_amount
        if self.total_amount < 0:
            self.total_amount = Decimal('0.00') # Tutar negatif olamaz
        self.save(update_fields=['total_amount'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Sipariş")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="Ürün")
    quantity = models.IntegerField(default=1, verbose_name="Miktar")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Fiyatı") # Ürünün sipariş anındaki fiyatı

    class Meta:
        verbose_name = "Sipariş Kalemi"
        verbose_name_plural = "Sipariş Kalemleri"
        unique_together = ('order', 'product') # <<<<< BU KISITLAMA VAR, JS VE VIEWS'DA YÖNETİYORUZ.

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Silinmiş Ürün'}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price