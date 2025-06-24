# musteri_takip_sistemi/settings.py

# ... (üst kısımlar aynı kalacak)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'core',
    'customers', # YENİ EKLENEN SATIR
    # 'orders',
    # 'stock',
    # 'customer_panel',
    # 'reports',
    # 'dashboard',
    # 'notifications',
    # 'messages_app',
    # 'settings_app',
]

# ... (alt kısımlar aynı kalacak)