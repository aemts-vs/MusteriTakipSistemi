# views.py (core ve stock view'larının birleştirilmiş hali)

# --- Gerekli Import'lar ---
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView

# Uygulama modelleri ve formları
from core.forms import (
    CustomerRegistrationForm,
    UserProfileForm,
    PersonnelAddForm,
    CustomPasswordChangeForm
)
from core.models import User
from stock.models import Product


# --- Yetkilendirme Mixin'leri ---
class AdminRequiredMixin(UserPassesTestMixin):
    """Sadece yönetici rolündeki kullanıcıların erişebilmesini sağlar."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin()

    def handle_no_permission(self):
        messages.error(self.request, "Bu sayfayı görüntülemek için yönetici yetkiniz yok.")
        return redirect('home')

class PersonnelRequiredMixin(UserPassesTestMixin):
    """Personel veya yönetici rolündeki kullanıcıların erişebilmesini sağlar."""
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_personnel() or self.request.user.is_admin())

    def handle_no_permission(self):
        messages.error(self.request, "Bu sayfayı görüntülemek için personel veya yönetici yetkiniz yok.")
        return redirect('home')

class CustomerRequiredMixin(UserPassesTestMixin):
    """Sadece müşteri rolündeki kullanıcıların erişebilmesini sağlar."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_customer()

    def handle_no_permission(self):
        messages.error(self.request, "Bu sayfayı görüntülemek için müşteri yetkiniz yok.")
        return redirect('home')


# --- Core (Çekirdek) Uygulama Görünümleri ---

def home(request):
    """Giriş (Karşılama) ekranı."""
    return render(request, 'core/home.html')

class UserLoginView(LoginView):
    """Kullanıcı Giriş Sayfası."""
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Geçersiz kullanıcı adı veya şifre.")
        return super().form_invalid(form)

class UserRegisterView(CreateView):
    """Yeni Müşteri Üye Olma Sayfası."""
    model = User
    form_class = CustomerRegistrationForm
    template_name = 'core/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Hesabınız başarıyla oluşturuldu. Şimdi giriş yapabilirsiniz.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Kayıt sırasında bir hata oluştu. Lütfen bilgileri kontrol edin.")
        return super().form_invalid(form)

class UserLogoutView(LogoutView):
    """Kullanıcı Çıkış İşlemi."""
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "Oturumunuz güvenli bir şekilde kapatıldı.")
        return super().dispatch(request, *args, **kwargs)

# --- Şifre Sıfırlama Görünümleri ---
class CustomPasswordResetView(PasswordResetView):
    template_name = 'core/password_reset_form.html'
    email_template_name = 'core/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    subject_template_name = 'core/password_reset_subject.txt'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'core/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'core/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'core/password_reset_complete.html'

# --- Şifre Değiştirme ve Profil Ayarları Görünümleri ---
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'core/password_change_form.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('profile_settings')

    def form_valid(self, form):
        messages.success(self.request, "Şifreniz başarıyla değiştirildi.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Şifre değiştirilirken bir hata oluştu. Lütfen bilgileri kontrol edin.")
        return super().form_invalid(form)

class ProfileSettingsView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'core/profile_settings.html'
    success_url = reverse_lazy('profile_settings')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil bilgileriniz başarıyla güncellendi.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Profil bilgileri güncellenirken bir hata oluştu. Lütfen bilgileri kontrol edin.")
        return super().form_invalid(form)

# --- Yönetim Paneli Görünümleri ---
class AdminPersonnelManagementView(AdminRequiredMixin, CreateView):
    """Yöneticilerin yeni personel ekleyebileceği sayfa."""
    model = User
    form_class = PersonnelAddForm
    template_name = 'core/admin_personnel_add.html'
    success_url = reverse_lazy('home') # Personel eklendikten sonra yönlendirilecek sayfa

    def form_valid(self, form):
        messages.success(self.request, "Yeni personel başarıyla eklendi.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Personel eklenirken bir hata oluştu. Lütfen bilgileri kontrol edin.")
        return super().form_invalid(form)


# --- Stock (Stok) Uygulaması Görünümleri ---

class ProductListView(PersonnelRequiredMixin, ListView):
    """
    Ürünleri listeleyen, filtreleyen ve sayfalayan görünüm.
    Sadece personel ve yöneticiler erişebilir.
    """
    model = Product
    template_name = 'stock/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name') # Varsayılan sıralama: isme göre

        # URL'den gelen 'status' parametresine göre filtreleme yap
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        # Eğer status 'all' ise veya hiç belirtilmemişse tüm ürünler listelenir.

        return queryset

    def get_context_data(self, **kwargs):
        # Şablonda hangi filtrenin aktif olduğunu göstermek için context'e ek bilgi gönder.
        context = super().get_context_data(**kwargs)
        context['current_status_filter'] = self.request.GET.get('status', 'all')
        return context