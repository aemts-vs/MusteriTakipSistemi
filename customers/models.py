# customers/models.py
from django.db import models

# Müşteri bilgileri doğrudan core.User modelinde yönetildiği için
# bu uygulamada yeni bir model tanımlamasına gerek yoktur.
# Sadece var olan User modelini filtreleyerek kullanacağız.