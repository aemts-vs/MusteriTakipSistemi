# notifications/views.py
from django.shortcuts import render, redirect, get_object_or_404 # <<<<<< get_object_or_404 eklendi
from django.views.generic import ListView, View
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Notification
from core.models import User # User modelini almak için
from core.views import PersonnelRequiredMixin, CustomerRequiredMixin # Yetkilendirme mixinleri


class UserNotificationListView(LoginRequiredMixin, ListView):
    """
    Giriş yapmış kullanıcının (admin, personel, müşteri) bildirimlerini listeler.
    """
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 15

    def get_queryset(self):
        # Admin ve personel tüm bildirimleri görebilir (veya kendi bildirimlerini de)
        if self.request.user.is_admin() or self.request.user.is_personnel():
            # Yöneticiler ve personeller, tüm sistem bildirimlerini görebilir.
            # Ancak, ilgili objeye göre filtrelemek daha anlamlı olabilir.
            # Şimdilik, kendi bildirimleri ve sipariş bildirimleri gibi genel bildirimler.
            # Daha gelişmiş senaryolarda, rollere göre farklı bildirim türlerini filtreleyebiliriz.
            # Basitçe tüm bildirimleri gösterelim, ancak ilgili bildirimin alıcısı admin/personel ise
            # veya bildirim tipi genel bir sistem bildirimi ise.
            return Notification.objects.all().order_by('-created_at')
        else: # Müşteriler sadece kendi bildirimlerini görür
            return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Bildirimler'
        # Okunmamış bildirim sayısını şablona gönderelim (navbar'da göstermek için)
        context['unread_notifications_count'] = self.get_queryset().filter(is_read=False).count()
        return context


class MarkNotificationAsReadView(LoginRequiredMixin, View):
    """
    Bildirimi okundu olarak işaretler.
    """
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        
        # Bildirimi sadece ilgili kişi veya bir yönetici/personel okundu olarak işaretleyebilir
        if notification.recipient == request.user or request.user.is_admin() or request.user.is_personnel():
            notification.mark_as_read()
            messages.success(request, "Bildirim okundu olarak işaretlendi.")
        else:
            messages.error(request, "Bu bildirimi okundu olarak işaretleme yetkiniz yok.")
        
        return redirect('notifications:user_notifications')

class MarkAllNotificationsAsReadView(LoginRequiredMixin, View):
    """
    Tüm bildirimleri okundu olarak işaretler.
    """
    def post(self, request):
        if request.user.is_admin() or request.user.is_personnel():
            Notification.objects.all().update(is_read=True) # Tüm bildirimleri okundu yap
        else:
            Notification.objects.filter(recipient=request.user).update(is_read=True) # Sadece kendi bildirimlerini okundu yap
        messages.success(request, "Tüm bildirimler okundu olarak işaretlendi.")
        return redirect('notifications:user_notifications')

def get_unread_notifications_count(request):
    """
    API endpoint'i gibi kullanılabilir, okunmamış bildirim sayısını döner.
    """
    if request.user.is_authenticated:
        if request.user.is_admin() or request.user.is_personnel():
            count = Notification.objects.filter(is_read=False).count() # Tüm okunmamışları sayabilir
        else:
            count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return JsonResponse({'count': count})
    return JsonResponse({'count': 0})