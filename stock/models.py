# stock/models.py

from django.db import models
import uuid  # Otomatik ürün kodu oluşturmak için eklendi

class Category(models.Model):
    """Ürün kategorilerini tanımlar."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategori Adı")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['name']

    def __str__(self):
        return self.name

class Supplier(models.Model):
    """Ürünlerin tedarik edildiği firmaları tanımlar."""
    name = models.CharField(max_length=200, unique=True, verbose_name="Firma Adı")
    address = models.TextField(blank=True, null=True, verbose_name="Adres")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telefon Numarası")
    email = models.EmailField(blank=True, null=True, verbose_name="E-posta Adresi")
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="İlgili Kişi")
    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")

    class Meta:
        verbose_name = "Tedarikçi"
        verbose_name_plural = "Tedarikçiler"
        ordering = ['name']

    def __str__(self):
        return self.name

class Warehouse(models.Model):
    """Ürünlerin saklandığı depoları tanımlar."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Depo Adı")
    address = models.TextField(verbose_name="Depo Adresi")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    class Meta:
        verbose_name = "Depo"
        verbose_name_plural = "Depolar"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    """Stok takibi yapılacak ürünleri tanımlar."""
    product_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Ürün Kodu")
    name = models.CharField(max_length=255, verbose_name="Ürün Adı")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="Kategori")
    current_stock = models.IntegerField(default=0, verbose_name="Mevcut Stok")
    minimum_stock = models.IntegerField(default=0, verbose_name="Minimum Stok (Kritik Seviye)")
    warehouse_location = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="Depo Konumu")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Maliyet (TL)")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Satış Fiyatı (TL)")
    #discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="İndirim Oranı (%)", help_text="Yüzde olarak indirim oranı (örn: 10.00 için %10)")
    main_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='supplied_products', verbose_name="Ana Tedarikçi")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Ürün Görseli")
    description = models.TextField(blank=True, null=True, verbose_name="Ürün Açıklaması")
    is_active = models.BooleanField(default=True, verbose_name="Satışa Açık (Aktif)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ['name']

    def save(self, *args, **kwargs):
        """
        Kaydetme metodunu override ederek, eğer ürün kodu boşsa otomatik atama yap.
        """
        if not self.product_code:
            # Otomatik ürün kodu oluşturma (örnek: Rastgele 10 karakterlik UUID)
            self.product_code = str(uuid.uuid4()).upper()[:10].replace('-', '')
        super().save(*args, **kwargs)

    def __str__(self):
        # Ürün kodu henüz oluşmamışsa (kaydedilmeden önce) bile hata vermez.
        return f"{self.name} ({self.product_code or 'Kod Bekleniyor'})"

    @property
    def is_low_stock(self):
        """Mevcut stokun kritik seviyenin altında olup olmadığını kontrol eder."""
        if self.minimum_stock > 0:
            return self.current_stock <= self.minimum_stock
        return False
  