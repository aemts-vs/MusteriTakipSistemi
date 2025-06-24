# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports' # Bu uygulama için bir namespace belirliyoruz

urlpatterns = [
    path('', views.ReportListView.as_view(), name='report_list'),
]