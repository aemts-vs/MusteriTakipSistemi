# dashboard/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Sum, Count, F # <<<<<< F'i buraya ekledik!
from django.utils import timezone
from datetime import timedelta

from core.views import AdminRequiredMixin
from core.models import User
from orders.models import Order
from stock.models import Product # Product modelini import etmiştik, ama F() için models objesine ihtiyacımız var.

# Django'nun genel models nesnesini import edelim
from django.db import models as db_models # <<<<<< db.models'ı db_models olarak import ettik


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Toplam Müşteri
        context['total_customers'] = User.objects.filter(user_type='customer').count()

        # Aktif Siparişler (Yeni, Kabul Edildi, Kargoya Verildi)
        context['active_orders_count'] = Order.objects.filter(
            order_status__in=['new', 'accepted', 'shipped']
        ).count()

        # Son 7 Gün Ciro
        seven_days_ago = timezone.now() - timedelta(days=7)
        context['last_7_days_revenue'] = Order.objects.filter(
            order_date__gte=seven_days_ago,
            order_status='delivered'
        ).aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0.00

        # Düşük Stoklu Ürünler (Burada db_models.F kullanıyoruz)
        context['low_stock_products_count'] = Product.objects.filter(
            is_active=True,
            current_stock__lte=db_models.F('minimum_stock') # <<<<< BURADA KULLANDIK
        ).count()

        # Son Siparişler (En Son 5 Sipariş)
        context['latest_orders'] = Order.objects.all().order_by('-order_date')[:5]

        context['page_title'] = 'Yönetici Paneli'
        return context