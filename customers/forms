# customers/forms.py
from django import forms
from core.models import User # core uygulamasındaki User modelini import ediyoruz

class CustomerEditForm(forms.ModelForm):
    # Bu form, sadece personel ve yöneticilerin müşterinin temel bilgilerini düzenlemesi içindir.
    # Şifre veya kullanıcı adı gibi hassas bilgiler buraya dahil edilmemeli.
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'company_name', 'address', 'customer_segment', 'date_of_birth',
            'notes', 'tax_id_number', 'payment_preference', 'debt_status',
            'is_active' # Müşteriyi pasife almak için 'is_active' alanı
        ]
        labels = {
            'first_name': 'Adı',
            'last_name': 'Soyadı',
            'email': 'E-posta Adresi',
            'phone_number': 'Telefon Numarası',
            'company_name': 'Firma Adı',
            'address': 'Adres',
            'customer_segment': 'Müşteri Türü',
            'date_of_birth': 'Doğum Tarihi',
            'notes': 'Notlar',
            'tax_id_number': 'Vergi/Kimlik Numarası',
            'payment_preference': 'Ödeme Tercihi',
            'debt_status': 'Borç Durumu',
            'is_active': 'Aktif Mi?'
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3})
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        # Eğer e-posta değiştiyse ve yeni e-posta başka bir kullanıcı tarafından kullanılıyorsa hata ver.
        # Current instance'ın kendi e-postası ise hata verme.
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor.")
        return email