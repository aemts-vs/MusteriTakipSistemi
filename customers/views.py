# customers/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from core.models import User # core uygulamasındaki User modelini kullanıyoruz
from core.views import PersonnelRequiredMixin # core'dan yetkilendirme mixin'imizi alıyoruz
from .forms import CustomerEditForm

class CustomerListView(PersonnelRequiredMixin, ListView):
    """
    Kayıtlı tüm müşterilerin listesini gösterir.
    Sadece personel ve yöneticiler erişebilir.
    """
    model = User
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10 # Sayfa başına 10 müşteri göster

    def get_queryset(self):
        # Sadece müşteri tipi kullanıcıları ve is_active True olanları göster
        # Yönetici, hem aktif hem pasif müşterileri görebilir, Personel sadece aktifleri görebilir.
        queryset = User.objects.filter(user_type='customer').order_by('-date_joined')
        if self.request.user.is_personnel() and not self.request.user.is_admin():
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Müşteri Listesi'
        return context

class CustomerDetailView(PersonnelRequiredMixin, DetailView):
    """
    Bir müşterinin detaylı bilgilerini gösterir.
    Sadece personel ve yöneticiler erişebilir.
    """
    model = User
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'
    pk_url_kwarg = 'pk' # URL'deki primary key parametresinin adı

    def get_queryset(self):
        # Sadece müşteri tipi kullanıcıları göstermek için
        return User.objects.filter(user_type='customer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"{self.object.first_name} {self.object.last_name} Detay"
        return context

class CustomerUpdateView(PersonnelRequiredMixin, UpdateView):
    """
    Bir müşterinin bilgilerini düzenlemeyi sağlar.
    Sadece personel ve yöneticiler erişebilir.
    """
    model = User
    form_class = CustomerEditForm
    template_name = 'customers/customer_form.html'
    context_object_name = 'customer'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        # Sadece müşteri tipi kullanıcıları düzenlemek için
        return User.objects.filter(user_type='customer')

    def get_success_url(self):
        messages.success(self.request, "Müşteri bilgileri başarıyla güncellendi.")
        return reverse_lazy('customers:customer_detail', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        messages.error(self.request, "Müşteri bilgileri güncellenirken bir hata oluştu. Lütfen bilgileri kontrol edin.")
        return super().form_invalid(form)

def customer_deactivate(request, pk):
    """
    Bir müşteriyi pasife alır (is_active=False yapar).
    Sadece personel ve yöneticiler erişebilir.
    """
    # Yetkilendirme kontrolü (PersonnelRequiredMixin gibi elle yapıldı çünkü fonksiyon tabanlı görünüm)
    if not request.user.is_authenticated or not (request.user.is_personnel() or request.user.is_admin()):
        messages.error(request, "Bu işlemi gerçekleştirmek için yetkiniz yok.")
        return redirect('home')

    customer = get_object_or_404(User, pk=pk, user_type='customer')

    if request.method == 'POST':
        customer.is_active = False
        customer.save()
        messages.success(request, f"{customer.first_name} {customer.last_name} adlı müşteri başarıyla pasife alındı.")
        return redirect('customers:customer_list')
    
    # POST dışındaki isteklerde (örn. GET) müşteriyi pasife alma onayı isteyebiliriz.
    messages.info(request, "Müşteriyi pasife almak için onay bekliyor.") # Bu mesaj kullanıcıya görünmez
    return redirect('customers:customer_detail', pk=pk) # GET isteğinde detay sayfasına yönlendir

def customer_activate(request, pk):
    """
    Bir müşteriyi aktife alır (is_active=True yapar).
    Sadece personel ve yöneticiler erişebilir.
    """
    if not request.user.is_authenticated or not (request.user.is_personnel() or request.user.is_admin()):
        messages.error(request, "Bu işlemi gerçekleştirmek için yetkiniz yok.")
        return redirect('home')

    customer = get_object_or_404(User, pk=pk, user_type='customer')

    if request.method == 'POST':
        customer.is_active = True
        customer.save()
        messages.success(request, f"{customer.first_name} {customer.last_name} adlı müşteri başarıyla aktife alındı.")
        return redirect('customers:customer_list')

    messages.info(request, "Müşteriyi aktife almak için onay bekliyor.") # Bu mesaj kullanıcıya görünmez
    return redirect('customers:customer_detail', pk=pk) # GET isteğinde detay sayfasına yönlendir