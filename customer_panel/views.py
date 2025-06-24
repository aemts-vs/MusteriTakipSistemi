# customer_panel/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from orders.models import Order, OrderItem
from stock.models import Product
from core.views import CustomerRequiredMixin # Sadece müşteri rolündeki kullanıcıların erişimi için
from django.db import transaction # Atomik işlemler için
from decimal import Decimal # DecimalField için

class CustomerDashboardView(CustomerRequiredMixin, ListView):
    """
    Müşterinin kendi siparişlerini listelediği panel sayfası.
    """
    model = Order
    template_name = 'customer_panel/customer_dashboard.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        # Sadece giriş yapmış müşterinin pasif olmayan siparişlerini göster
        return Order.objects.filter(
            customer=self.request.user,
            order_status__in=['new', 'accepted', 'shipped', 'delivered', 'cancelled', 'returned'] # passive olmayanlar
        ).order_by('-order_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Müşteri Paneli'
        return context

class CustomerOrderDetailView(CustomerRequiredMixin, DetailView):
    """
    Müşterinin kendi siparişinin detaylarını gördüğü sayfa.
    """
    model = Order
    template_name = 'customer_panel/customer_order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        # Sadece giriş yapmış müşterinin siparişlerini göster
        return Order.objects.filter(customer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Sipariş Detayı: {self.object.order_id}"
        return context

# --- Alışveriş Bölümü ---
class ShopProductListView(CustomerRequiredMixin, ListView):
    """
    Müşterilerin alışveriş yapabileceği ürün listesi sayfası.
    Sadece aktif ve stokta olan ürünleri gösterir.
    """
    model = Product
    template_name = 'customer_panel/shop_product_list.html'
    context_object_name = 'products'
    paginate_by = 12 # Sayfa başına 12 ürün göster

    def get_queryset(self):
        # Sadece aktif ve stokta olan ürünleri göster
        queryset = super().get_queryset().filter(is_active=True, current_stock__gt=0).order_by('name')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Ürün Kataloğu'
        return context

class AddToCartView(CustomerRequiredMixin, View):
    """
    Ürünleri sepete ekler (oturum tabanlı sepet).
    """
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            messages.error(request, "Ürün miktarı 1'den az olamaz.")
            return redirect('customer_panel:shop_product_list')

        if product.current_stock < quantity:
            messages.error(request, f"'{product.name}' ürünü için yeterli stok bulunmamaktadır. Mevcut stok: {product.current_stock} adet.")
            return redirect('customer_panel:shop_product_list')

        # Sepeti oturumda tut
        cart = request.session.get('cart', {})
        product_id_str = str(pk) # JSON uyumluluğu için string anahtar

        # Sepette ürün zaten varsa miktarı artır
        if product_id_str in cart:
            new_quantity = cart[product_id_str]['quantity'] + quantity
            if product.current_stock < new_quantity: # Yeni toplam miktarı stokla kontrol et
                 messages.error(request, f"Sepetinizdeki '{product.name}' için toplam miktar ({new_quantity}) stoktan fazla. Mevcut stok: {product.current_stock} adet.")
                 return redirect('customer_panel:shop_product_list')
            cart[product_id_str]['quantity'] = new_quantity
        else:
            cart[product_id_str] = {
                'product_id': pk,
                'name': product.name,
                'unit_price': str(product.selling_price), # Decimal'ı string olarak sakla
                'quantity': quantity,
                'image_url': product.image.url if product.image else None,
                'product_code': product.product_code,
            }
        
        request.session['cart'] = cart
        messages.success(request, f"{quantity} adet '{product.name}' sepete eklendi.")
        return redirect('customer_panel:shop_product_list') # Genellikle sepete eklendikten sonra ürün listesine dönülür

class CartView(CustomerRequiredMixin, View):
    """
    Müşterinin sepetini görüntülediği ve düzenlediği sayfa.
    """
    template_name = 'customer_panel/cart.html'

    def get(self, request):
        cart = request.session.get('cart', {})
        cart_items = []
        total_cart_price = Decimal(0)

        for product_id_str, item_data in cart.items():
            product_id = int(product_id_str)
            product = get_object_or_404(Product, pk=product_id) # Ürünün güncel halini alalım
            
            # Stok kontrolü yap, eğer stok değişmişse uyarı ver
            if item_data['quantity'] > product.current_stock:
                messages.warning(request, f"Sepetinizdeki '{product.name}' ürününde yeterli stok kalmadı. Mevcut stok: {product.current_stock} adet.")
                # Miktarı stok miktarına düşürebiliriz veya tamamen sepetten çıkarabiliriz.
                item_data['quantity'] = product.current_stock # Miktarı düzelt
                if product.current_stock == 0:
                    del request.session['cart'][product_id_str] # Stok yoksa sepetten sil
                    messages.error(request, f"Sepetinizdeki '{product.name}' ürünü stokta kalmadığı için sepetten çıkarıldı.")
                    request.session.modified = True # Oturumu kaydet
                    continue
            
            # Ürünün güncel fiyatını kullan (veya sipariş anındaki fiyatını koru)
            item_price = Decimal(item_data['unit_price']) # Sepete eklerken kaydedilen fiyatı kullan
            total_item_price = item_price * item_data['quantity']
            total_cart_price += total_item_price

            cart_items.append({
                'product_id': product_id,
                'name': item_data['name'],
                'unit_price': item_price,
                'quantity': item_data['quantity'],
                'total_price': total_item_price,
                'image_url': item_data['image_url'],
                'product_code': item_data['product_code'],
            })
        
        # Güncellenmiş sepeti oturuma geri yaz (eğer değişiklik olduysa)
        request.session['cart'] = cart
        request.session.modified = True # Oturumun değiştiğini işaretle

        return render(request, self.template_name, {
            'cart_items': cart_items,
            'total_cart_price': total_cart_price,
            'page_title': 'Sepetim'
        })

    def post(self, request):
        # Sepet miktarını güncelle veya ürünü sepetten çıkar
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        cart = request.session.get('cart', {})

        if product_id not in cart:
            messages.error(request, "Ürün sepetinizde bulunamadı.")
            return redirect('customer_panel:cart_view')

        product_id_str = str(product_id)
        product = get_object_or_404(Product, pk=product_id)

        if action == 'update_quantity':
            try:
                new_quantity = int(request.POST.get('quantity'))
                if new_quantity <= 0:
                    del cart[product_id_str] # Miktar 0 veya altıysa sepetten çıkar
                    messages.info(request, f"'{product.name}' sepetinizden kaldırıldı.")
                else:
                    # Stok kontrolü
                    if product.current_stock < new_quantity:
                        messages.error(request, f"'{product.name}' ürünü için yeterli stok bulunmamaktadır. Mevcut stok: {product.current_stock} adet.")
                        return redirect('customer_panel:cart_view')
                    cart[product_id_str]['quantity'] = new_quantity
                    messages.success(request, f"'{product.name}' miktarı güncellendi.")
            except ValueError:
                messages.error(request, "Geçersiz miktar.")
        elif action == 'remove':
            del cart[product_id_str]
            messages.info(request, f"'{product.name}' sepetinizden kaldırıldı.")
        
        request.session['cart'] = cart
        request.session.modified = True
        return redirect('customer_panel:cart_view')

class CheckoutView(CustomerRequiredMixin, View):
    """
    Sepetteki ürünleri sipariş olarak oluşturan ve stoğu güncelleyen sayfa.
    """
    template_name = 'customer_panel/checkout.html' # Boş bir ödeme sayfası

    def get(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            messages.warning(request, "Sepetiniz boş. Lütfen önce ürün ekleyin.")
            return redirect('customer_panel:shop_product_list')

        cart_items_for_display = []
        total_price = Decimal(0)
        
        # Stokları tekrar kontrol et
        for product_id_str, item_data in cart.items():
            product = get_object_or_404(Product, pk=int(product_id_str))
            if item_data['quantity'] > product.current_stock:
                messages.error(request, f"'{product.name}' ürünü için yeterli stok bulunmamaktadır. Mevcut stok: {product.current_stock} adet. Lütfen sepeti güncelleyin.")
                return redirect('customer_panel:cart_view') # Stok sorunu varsa sepete geri yolla

            item_price = Decimal(item_data['unit_price'])
            total_item_price = item_price * item_data['quantity']
            total_price += total_item_price
            
            cart_items_for_display.append({
                'product': product,
                'quantity': item_data['quantity'],
                'unit_price': item_price,
                'total_price': total_item_price
            })

        # Müşterinin adresini varsayılan olarak al (eğer varsa)
        initial_delivery_address = self.request.user.address if self.request.user.address else ""

        return render(request, self.template_name, {
            'cart_items': cart_items_for_display,
            'total_price': total_price,
            'initial_delivery_address': initial_delivery_address,
            'page_title': 'Ödeme Sayfası'
        })


    def post(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Sepetiniz boş.")
            return redirect('customer_panel:shop_product_list')

        delivery_address = request.POST.get('delivery_address', self.request.user.address)
        payment_method = request.POST.get('payment_method', 'cash_on_delivery') # Varsayılan ödeme yöntemi

        if not delivery_address:
            messages.error(request, "Teslimat adresi boş bırakılamaz.")
            # Burada formu tekrar render edip hata gösterebiliriz.
            # Şimdilik sadece mesaj verip sepete dönelim
            return redirect('customer_panel:checkout')

        try:
            with transaction.atomic():
                # Sipariş oluştur
                order = Order.objects.create(
                    customer=request.user,
                    delivery_address=delivery_address,
                    payment_method=payment_method,
                    order_status='new', # Yeni sipariş olarak başlat
                    payment_status='pending', # Ödeme bekleniyor
                    total_amount=Decimal(0) # Başlangıçta 0, OrderItem'lar eklenince güncellenecek
                )

                total_order_price = Decimal(0)
                for product_id_str, item_data in cart.items():
                    product = get_object_or_404(Product, pk=int(product_id_str))
                    quantity = item_data['quantity']
                    unit_price = Decimal(item_data['unit_price'])

                    # Son stok kontrolü
                    if product.current_stock < quantity:
                        raise ValueError(f"'{product.name}' ürününde yeterli stok kalmadı. Mevcut: {product.current_stock} adet. Lütfen sepeti güncelleyin.")

                    # OrderItem oluştur
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price
                    )

                    # Stoktan düş
                    product.current_stock -= quantity
                    product.save()
                    total_order_price += quantity * unit_price
                
                # Siparişin toplam tutarını güncelle (İndirim vb. daha sonra eklenebilir)
                order.total_amount = total_order_price
                order.save()

                # Sepeti temizle
                del request.session['cart']
                request.session.modified = True

                messages.success(request, f"Siparişiniz ({order.order_id}) başarıyla oluşturuldu!")
                return redirect('customer_panel:customer_order_detail', pk=order.pk)

        except ValueError as e:
            messages.error(request, f"Sipariş oluşturulurken hata: {e}")
            return redirect('customer_panel:cart_view')
        except Exception as e:
            messages.error(request, f"Beklenmedik bir hata oluştu: {e}")
            return redirect('customer_panel:cart_view')