# reports/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count, Sum # Veritabanı sorguları için
from django.db.models.functions import TruncMonth # Aylara göre gruplama için
from datetime import datetime, timedelta # Tarih işlemleri için
from django.utils import timezone # Tarih işlemleri için
from core.views import PersonnelRequiredMixin # Yetkilendirme için
from orders.models import Order, OrderItem # Sipariş verileri için
from stock.models import Product # Ürün verileri için

class ReportListView(PersonnelRequiredMixin, TemplateView):
    template_name = 'reports/report_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # --- Aylara Göre Sipariş Sayısı ---
        # Sadece tamamlanmış siparişleri (delivered, returned, cancelled) alalım
        monthly_orders = Order.objects.filter(
            order_status__in=['delivered', 'returned', 'cancelled']
        ).annotate(
            month=TruncMonth('order_date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        monthly_labels = [order['month'].strftime('%Y-%m') for order in monthly_orders]
        monthly_data = [order['count'] for order in monthly_orders]

        context['monthly_order_labels'] = monthly_labels
        context['monthly_order_data'] = monthly_data

        # --- En Çok Satan Ürünler ---
        top_selling_products = OrderItem.objects.values('product__name').annotate(
            total_quantity_sold=Sum('quantity')
        ).order_by('-total_quantity_sold')[:5] # İlk 5 ürün

        top_product_labels = [item['product__name'] for item in top_selling_products]
        top_product_data = [item['total_quantity_sold'] for item in top_selling_products]

        context['top_product_labels'] = top_product_labels
        context['top_product_data'] = top_product_data

        context['page_title'] = 'Raporlar'
        return context