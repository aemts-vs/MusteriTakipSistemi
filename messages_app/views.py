# messages_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Message, MessageReply
from .forms import MessageForm, MessageReplyForm
from core.views import AdminRequiredMixin, PersonnelRequiredMixin, CustomerRequiredMixin # Yetkilendirme mixinleri
from core.models import User # Bildirim göndermek için
from notifications.models import create_notification # Bildirim oluşturmak için

# --- Mesaj Gönderme (Müşteri İçin) ---
class SendMessageView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'messages_app/send_message.html'
    success_url = reverse_lazy('messages_app:message_list') # Gönderilen mesajlar listesine yönlendir

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # Formu, giriş yapmış kullanıcıya göre filtrelemek için
        return kwargs

    def form_valid(self, form):
        form.instance.sender = self.request.user
        
        # Alıcı belirle: Yöneticiler veya Personeller
        # Şimdilik, gönderilen tüm mesajları tüm personel ve yöneticilere ulaştıralım.
        # Daha karmaşık bir senaryoda, departman veya atanmış kişiye göre yönlendirme yapılabilir.
        # Örneğin, recipient alanını boş bırakıp, MessageListView'de recipient is null olanları tüm personele göster.
        # Ya da varsayılan bir destek hesabına yönlendirebiliriz.
        # Basitlik adına, şimdilik bu alanı boş bırakalım ve tüm yetkililer görebilsin.
        
        response = super().form_valid(form)
        messages.success(self.request, "Mesajınız başarıyla gönderildi.")

        # Personel/Yöneticilere yeni mesaj bildirimi gönder
        for staff_user in User.objects.filter(user_type__in=['admin', 'personnel']):
            create_notification(staff_user, f"Yeni bir mesajınız var: '{self.object.subject}'", 'new_message', self.object)

        return response

    def form_invalid(self, form):
        messages.error(self.request, "Mesaj gönderilirken bir hata oluştu. Lütfen bilgileri kontrol edin.")
        return super().form_invalid(form)


# --- Mesajları Listeleme ---
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'messages_app/message_list.html'
    context_object_name = 'messages'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_admin():
            # Yöneticiler tüm mesajları görsün
            return Message.objects.all().order_by('-created_at')
        elif self.request.user.is_personnel():
            # Personeller sadece 'request' (talep) tipindeki mesajları ve kendilerine gönderilenleri görsün
            # Şu an için recipient field'ını boş bıraktığımız için, tüm mesajları görecekler, ancak tipine göre filtreleyebiliriz.
            # "talep mesajlarını sadece personel görsün" gereksinimi için
            return Message.objects.filter(message_type='request').order_by('-created_at') # Sadece talep mesajları
        else: # Müşteriler sadece kendi gönderdikleri mesajları görsün
            return Message.objects.filter(sender=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Mesajlarım' if self.request.user.is_customer() else 'Tüm Mesajlar'
        return context


# --- Mesaj Detay ve Yanıtlama ---
class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'messages_app/message_detail.html'
    context_object_name = 'message'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        # Yetkilendirme:
        # Admin: Tüm mesajları
        # Personel: İlgili mesaj tipindeki mesajları
        # Müşteri: Sadece kendi gönderdiği mesajları
        if self.request.user.is_admin():
            return Message.objects.all()
        elif self.request.user.is_personnel():
            return Message.objects.filter(message_type='request') # Sadece talep mesajları
        else: # Müşteri
            return Message.objects.filter(sender=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Mesaj Detayı: {self.object.subject}"
        context['reply_form'] = MessageReplyForm() # Yanıt formu
        # Mesajı okundu olarak işaretle (eğer alıcı bu kullanıcıysa ve okunmadıysa)
        if self.request.user == self.object.recipient and not self.object.is_read_by_recipient:
            self.object.mark_as_read()
        return context

class MessageReplyView(LoginRequiredMixin, View):
    """
    Mesaja yanıt gönderme.
    """
    def post(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        form = MessageReplyForm(request.POST)

        # Yanıt gönderme yetkilendirmesi: Mesajın göndereni, alıcısı veya admin/personel
        if not (request.user == message.sender or \
                request.user == message.recipient or \
                request.user.is_admin() or \
                request.user.is_personnel()):
            messages.error(request, "Bu mesaja yanıt verme yetkiniz yok.")
            return redirect('messages_app:message_detail', pk=pk)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.message = message
            reply.sender = request.user
            reply.save()

            message.status = 'replied' # Mesaj durumunu cevaplandı olarak işaretle
            message.is_read_by_recipient = False # Yanıt geldiğinde diğer taraf için okunmadı yap
            message.save()

            messages.success(request, "Yanıtınız başarıyla gönderildi.")

            # Diğer tarafa bildirim gönder (mesajın asıl göndericisi veya alıcısı)
            recipient_for_notification = message.sender if request.user != message.sender else message.recipient
            if recipient_for_notification:
                create_notification(recipient_for_notification, f"Mesajınız ({message.subject}) cevaplandı.", 'new_message', message)

        else:
            messages.error(request, "Yanıt gönderilirken bir hata oluştu.")
        
        return redirect('messages_app:message_detail', pk=pk)