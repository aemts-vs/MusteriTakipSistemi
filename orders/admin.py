# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline): # Sipariş detay sayfasında OrderItem'ları göstermek için
    model = OrderItem
    extra = 0 # Varsayılan olarak kaç boş form göstereceği
    raw_id_fields = ('product',) # Ürün seçimi için arama kutucuğu kullanır
    readonly_fields = ('unit_price',) # Birim fiyatı manuel değiştirilmesin

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline] # OrderItem'ları Order'ın içinde gösterir

    list_display = (
        'order_id', 'customer', 'order_date', 'order_status',
        'total_amount', 'payment_status', 'shipping_company', 'is_completed'
    )
    list_filter = (
        'order_status', 'payment_status', 'payment_method',
        'shipping_company', 'is_completed', 'order_date'
    )
    search_fields = (
        'order_id', 'customer__username', 'customer__first_name',
        'customer__last_name', 'delivery_address', 'tracking_number'
    )
    raw_id_fields = ('customer',) # Müşteri seçimi için arama kutucuğu kullanır
    date_hierarchy = 'order_date' # Tarihe göre filtreleme widget'ı
    ordering = ('-order_date',)
    readonly_fields = ('order_id', 'created_at', 'updated_at') # Otomatik oluşturulan alanlar

    fieldsets = (
        (None, {
            'fields': ('order_id', 'customer', 'order_date', 'order_status', 'is_completed')
        }),
        ('Ödeme Bilgileri', {
            'fields': ('payment_status', 'payment_method', 'total_amount', 'discount_code', 'discount_amount')
        }),
        ('Teslimat Bilgileri', {
            'fields': ('delivery_address', 'shipping_company', 'tracking_number', 'estimated_delivery_date')
        }),
        ('Ek Notlar', {
            'fields': ('notes',)
        }),
        ('Zaman Damgaları', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Bu alanı varsayılan olarak kapalı gösterir
        }),
    )

    def save_formset(self, request, form, formset, change):
        # Bu metod, OrderItem'lar kaydedildikten sonra Order'ın toplam tutarını güncellemek için idealdir.
        # Önce formset'teki değişiklikleri kaydet, sonra Order'ı güncelle.
        formset.save() # OrderItem'ları kaydeder (yeni, güncellenmiş, silinmiş)
        form.instance.update_total_amount() # Order'ın toplam tutarını günceller
        super().save_formset(request, form, formset, change)

    def save_model(self, request, obj, form, change):
        # Order modelini kaydederken toplam tutarı güncelle
        super().save_model(request, obj, form, change)
        obj.update_total_amount() # Order kaydedilirken de toplamı güncelle