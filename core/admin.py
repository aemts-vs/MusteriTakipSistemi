# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Django'nun varsayılan UserAdmin'ini import ediyoruz
from .models import User # Kendi özel User modelimizi import ediyoruz
from notifications.models import create_notification # <<<<<< YENİ EKLENEN IMPORT

# Kendi UserAdmin sınıfımızı tanımlıyoruz
class CustomUserAdmin(UserAdmin):
    # Admin panelindeki kullanıcı değiştirme formunda gösterilecek alanları ayarlar.
    # UserAdmin'in varsayılan fieldsets'lerine kendi eklediğimiz alanları ekliyoruz.
    fieldsets = UserAdmin.fieldsets + (
        (('Ek Bilgiler'), {'fields': (
            'user_type', 'phone_number', 'company_name', 'address',
            'customer_segment', 'date_of_birth', 'notes', 'tax_id_number',
            'payment_preference', 'debt_status'
        )}),
    )

    # Admin panelindeki kullanıcı ekleme formunda gösterilecek alanları ayarlar.
    # add_fieldsets, UserAdmin'in kullanıcı oluşturma formları için kullandığı bir özelliktir.
    add_fieldsets = UserAdmin.add_fieldsets + (
        (('Ek Bilgiler'), {'fields': (
            'user_type', 'phone_number', 'company_name', 'address',
            'customer_segment', 'date_of_birth'
        )}),
    )

    # Listede görünecek alanlar
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active', 'debt_status') # <<<<<< debt_status eklendi
    # Filtreleme seçenekleri
    list_filter = ('user_type', 'is_staff', 'is_active')
    # Arama alanları
    search_fields = ('username', 'email', 'first_name', 'last_name', 'company_name')
    # Sıralama
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        # Eğer borç durumu değiştiyse bildirim gönder ve sadece müşteri ise
        if change and 'debt_status' in form.changed_data and obj.is_customer():
            old_debt = form.initial.get('debt_status', 0)
            new_debt = obj.debt_status
            message = f"Borç durumunuz güncellendi: {old_debt} TL'den {new_debt} TL'ye."
            create_notification(obj, message, 'debt_change', obj)
        super().save_model(request, obj, form, change)

# Kendi özel User modelimizi, özel UserAdmin sınıfımızla Django admin'e kaydediyoruz.
admin.site.register(User, CustomUserAdmin)