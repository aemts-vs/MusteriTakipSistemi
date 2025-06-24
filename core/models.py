# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ("admin", "Yönetici"),
        ("personnel", "Personel"),
        ("customer", "Müşteri"),
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="customer",
        verbose_name="Kullanıcı Tipi"
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Telefon Numarası"
    )
    company_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Firma Adı"
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Adres"
    )
    customer_segment = models.CharField(
        max_length=20,
        choices=[('individual', 'Bireysel'), ('corporate', 'Kurumsal')],
        blank=True,
        null=True,
        verbose_name="Müşteri Segmenti"
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name="Doğum Tarihi"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notlar"
    )
    tax_id_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Vergi/Kimlik Numarası"
    )
    payment_preference = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Ödeme Tercihi"
    )
    debt_status = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Borç Durumu"
    )


    def is_admin(self):
        return self.user_type == "admin"

    def is_personnel(self):
        return self.user_type == "personnel"

    def is_customer(self):
        return self.user_type == "customer"

    def get_user_type_display(self):
        return dict(self.USER_TYPE_CHOICES).get(self.user_type)

    def __str__(self):
        return self.username # veya self.get_full_name()