# musteri_takip_sistemi/urls.py
from django.contrib import admin
from django.urls import path, include # 'include' buraya eklendi (önceki hata çözümü)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # core uygulaması URL'lerini dahil et
    # Buraya ileride oluşturacağınız diğer uygulamaların URL'lerini ekleyeceksiniz:
    path('customers/', include('customers.urls')),
    path('stock/', include('stock.urls')),
    path('orders/', include('orders.urls')),
    path('panel/', include('customer_panel.urls')),
    path('reports/', include('reports.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('notifications/', include('notifications.urls')),
    path('mesajlar/', include('messages_app.urls')),
    path('ayarlar/', include('settings_app.urls')),
]
# Medya dosyalarını geliştirme ortamında sunmak için
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)