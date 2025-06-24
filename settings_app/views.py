# settings_app/views.py
from django.shortcuts import render, redirect
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from .models import UserPreferences
from .forms import UserPreferencesForm
from core.views import AdminRequiredMixin # Sadece yöneticiye özel sistem ayarları için


class ThemeSettingsView(LoginRequiredMixin, UpdateView):
    model = UserPreferences
    form_class = UserPreferencesForm
    template_name = 'settings_app/theme_settings.html'
    success_url = reverse_lazy('settings_app:theme_settings') # Aynı sayfaya yönlendir

    def get_object(self):
        # Kullanıcının tercihleri yoksa oluştur
        obj, created = UserPreferences.objects.get_or_create(user=self.request.user)
        return obj

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object() # Mevcut preference'ı forma bağla
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Tema ayarlarınız başarıyla kaydedildi.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Tema ayarları kaydedilirken bir hata oluştu.")
        return super().form_invalid(form)


# Navbar konumunu değiştirmek için basit bir view (JS ile de yapılabilir)
def change_navbar_position(request):
    if request.method == 'POST' and request.user.is_authenticated:
        position = request.POST.get('navbar_position')
        if position in ['top', 'side']:
            user_pref, created = UserPreferences.objects.get_or_create(user=request.user)
            user_pref.navbar_position = position
            user_pref.save()
            messages.success(request, f"Navbar konumu başarıyla '{position}' olarak ayarlandı.")
        else:
            messages.error(request, "Geçersiz navbar konumu seçimi.")
    return redirect(reverse_lazy('settings_app:theme_settings'))


# Otomatik çıkış (Auto Logout) için middleware daha sonra eklenecek.
# Şimdilik sadece ayarını yapıyoruz.