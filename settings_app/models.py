# settings_app/models.py
from django.db import models
from core.models import User # Kullanıcı tercihlerini bağlamak için

class UserPreferences(models.Model):
    THEME_CHOICES = (
        ('light', 'Açık Tema'),
        ('dark', 'Koyu Tema'),
        ('blue', 'Mavi Tema'),
        ('green', 'Yeşil Tema'),
        # Daha fazla tema eklenebilir
    )
    NAV_POS_CHOICES = (
        ('top', 'Üst Navbar'),
        ('side', 'Yan Sidebar'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences', verbose_name="Kullanıcı")
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='light', verbose_name="Tema")
    navbar_position = models.CharField(max_length=10, choices=NAV_POS_CHOICES, default='top', verbose_name="Navbar Konumu")
    
    # Otomatik oturum süresi ayarı (sadece yönetici için görünür olacak)
    auto_logout_minutes = models.IntegerField(default=30, verbose_name="Otomatik Çıkış Süresi (dk)")
    
    # Diğer sistem ayarları buraya eklenebilir
    # is_system_maintenance = models.BooleanField(default=False)
    # default_currency = models.CharField(max_length=5, default='TL')

    class Meta:
        verbose_name = "Kullanıcı Tercihi"
        verbose_name_plural = "Kullanıcı Tercihleri"

    def __str__(self):
        return f"{self.user.username}'ın Tercihleri"