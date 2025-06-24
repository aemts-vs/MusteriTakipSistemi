# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User

class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Adınız", max_length=150, required=True)
    last_name = forms.CharField(label="Soyadınız", max_length=150, required=True)
    email = forms.EmailField(label="E-posta Adresi", required=True)
    phone_number = forms.CharField(label="Telefon Numarası", max_length=15, required=True)
    company_name = forms.CharField(label="Firma Adı (Opsiyonel)", max_length=100, required=False)
    address = forms.CharField(label="Adres", widget=forms.Textarea(attrs={'rows': 3}), required=True)
    customer_segment = forms.ChoiceField(
        label="Müşteri Türü",
        choices=[('individual', 'Bireysel'), ('corporate', 'Kurumsal')],
        required=True
    )
    date_of_birth = forms.DateField(
        label="Doğum Tarihi (GG.AA.YYYY)",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%d.%m.%Y', '%Y-%m-%d']
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'email', 'phone_number',
            'company_name', 'address', 'customer_segment', 'date_of_birth'
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kullanılıyor.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.company_name = self.cleaned_data['company_name']
        user.address = self.cleaned_data['address']
        user.customer_segment = self.cleaned_data['customer_segment']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        user.user_type = "customer" # Üye olanlar varsayılan olarak müşteri tipindedir.

        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'company_name', 'address', 'date_of_birth', 'customer_segment']
        labels = {
            'first_name': 'Adınız',
            'last_name': 'Soyadınız',
            'email': 'E-posta Adresi',
            'phone_number': 'Telefon Numarası',
            'company_name': 'Firma Adı',
            'address': 'Adres',
            'date_of_birth': 'Doğum Tarihi',
            'customer_segment': 'Müşteri Türü',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }

class PersonnelAddForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Şifre")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Şifre Tekrar")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth', 'user_type']
        labels = {
            'username': 'Kullanıcı Adı',
            'first_name': 'Adı',
            'last_name': 'Soyadı',
            'email': 'E-posta',
            'phone_number': 'Telefon Numarası',
            'address': 'Adres',
            'date_of_birth': 'Doğum Tarihi',
            'user_type': 'Kullanıcı Rolü',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Şifreler eşleşmiyor.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class CustomPasswordChangeForm(PasswordChangeForm):
    pass