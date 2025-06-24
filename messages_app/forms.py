# messages_app/forms.py
from django import forms
from .models import Message, MessageReply
from orders.models import Order # Sipariş seçimi için

class MessageForm(forms.ModelForm):
    # Müşteriler için sipariş seçimi, sadece kendi siparişleri
    # Formun view'da oluşturulurken queryset dinamik olarak ayarlanacak
    order = forms.ModelChoiceField(
        queryset=Order.objects.none(), # Başlangıçta boş, view'da filtrelenecek
        label="İlgili Sipariş (Opsiyonel)",
        required=False,
        empty_label="Sipariş Seçin (Varsa)"
    )

    class Meta:
        model = Message
        fields = ['subject', 'message_type', 'order', 'content']
        labels = {
            'subject': 'Konu',
            'message_type': 'Mesaj Tipi',
            'order': 'İlgili Sipariş',
            'content': 'Mesaj İçeriği',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

    # Formu alan kullanıcının siparişlerini gösterecek şekilde dinamik olarak ayarla
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated and user.is_customer():
            self.fields['order'].queryset = Order.objects.filter(customer=user).order_by('-order_date')
        elif user and user.is_authenticated and (user.is_admin() or user.is_personnel()):
            self.fields['order'].queryset = Order.objects.all().order_by('-order_date')


class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = MessageReply
        fields = ['content']
        labels = {
            'content': 'Yanıtınız',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }