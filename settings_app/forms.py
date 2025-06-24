# settings_app/forms.py
from django import forms
from .models import UserPreferences

class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ['theme', 'navbar_position', 'auto_logout_minutes']
        labels = {
            'theme': 'Tema',
            'navbar_position': 'Navbar Konumu',
            'auto_logout_minutes': 'Otomatik Çıkış Süresi (dk)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece adminler auto_logout_minutes'ı görsün/düzenlesin
        if 'instance' in kwargs and kwargs['instance']:
            if not kwargs['instance'].user.is_admin():
                del self.fields['auto_logout_minutes']