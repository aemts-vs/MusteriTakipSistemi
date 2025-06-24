# customer_panel/urls.py
from django.urls import path
from . import views

app_name = 'customer_panel' # Bu uygulama için bir namespace belirliyoruz

urlpatterns = [
    path('', views.CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('orders/<int:pk>/', views.CustomerOrderDetailView.as_view(), name='customer_order_detail'),

    # Alışveriş sayfası URL'leri
    path('shop/', views.ShopProductListView.as_view(), name='shop_product_list'),
    path('add-to-cart/<int:pk>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', views.CartView.as_view(), name='cart_view'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
]