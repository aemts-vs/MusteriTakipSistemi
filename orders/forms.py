# orders/forms.py
from django import forms
from .models import Order, OrderItem
from core.models import User # Müşteri seçimi için User modelini kullanacağız
from stock.models import Product # Ürün seçimi için Product modelini kullanacağız
from django.forms import inlineformset_factory # Formset için

class OrderForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=User.objects.filter(user_type='customer', is_active=True), # Sadece aktif müşteriler listelensin
        label="Müşteri",
        required=True,
        empty_label="Müşteri Seçin"
    )

    class Meta:
        model = Order
        fields = [
            'customer', 'delivery_address', 'order_status',
            'payment_status', 'payment_method', 'shipping_company',
            'tracking_number', 'estimated_delivery_date',
            'discount_code', 'discount_amount', 'notes'
        ]
        labels = {
            'customer': 'Müşteri',
            'delivery_address': 'Teslimat Adresi',
            'order_status': 'Sipariş Durumu',
            'payment_status': 'Ödeme Durumu',
            'payment_method': 'Ödeme Yöntemi',
            'shipping_company': 'Kargo Firması',
            'tracking_number': 'Takip Numarası',
            'estimated_delivery_date': 'Tahmini Teslimat Tarihi',
            'discount_code': 'İndirim Kodu',
            'discount_amount': 'İndirim Tutarı',
            'notes': 'Notlar',
        }
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
            'estimated_delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    # OrderForm'da özel clean metoduna gerek yok, views.py'de yönetiliyor
    # clean metodu burada genellikle global doğrulama veya bağımlı alanlar için kullanılır
    # Tekrarlayan OrderItem kontrolü views.py'de daha iyi yönetilir.


class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True, current_stock__gt=0), # Sadece aktif ve stokta olan ürünler
        label="Ürün",
        required=True,
        empty_label="Ürün Seçin"
    )
    quantity = forms.IntegerField(min_value=1, label="Miktar")

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        labels = {
            'product': 'Ürün',
            'quantity': 'Miktar',
        }

    def clean_quantity(self): # Sadece miktar için clean metodu
        quantity = self.cleaned_data.get('quantity')
        product = self.cleaned_data.get('product')

        if product and quantity is not None:
            # Güncelleme durumunda eski miktarı da dikkate alarak stok kontrolü
            if self.instance.pk:
                old_quantity = self.instance.quantity
                available_stock = product.current_stock + old_quantity
            else: # Yeni OrderItem oluşturuluyorsa
                available_stock = product.current_stock

            if quantity > available_stock:
                raise forms.ValidationError(
                    f"'{product.name}' ürününde yeterli stok bulunmamaktadır. Mevcut: {available_stock} adet."
                )
        return quantity


# OrderForm ile OrderItemForm'u bir arada kullanmak için formsetler
# extra=0: Başlangıçta hiç boş form gösterme, hepsi JS ile eklensin
# can_delete=True: Formset'ten öğe silinebilmesini sağlar
OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=0, can_delete=True
)