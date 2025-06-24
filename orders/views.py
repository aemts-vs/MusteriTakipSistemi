# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db import transaction # İşlemleri atomik hale getirmek için
from decimal import Decimal # DecimalField için
from django.utils import timezone # Tarih işlemleri için (şimdilik kullanılmasa da genel pratik)

from .models import Order, OrderItem
from .forms import OrderForm, OrderItemFormSet
from core.views import PersonnelRequiredMixin
from stock.models import Product # Stok güncellemeleri için
from notifications.models import create_notification
from core.models import User # User modelini import ediyoruz


class OrderListView(PersonnelRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        # Yöneticiler tüm siparişleri, personeller pasif olmayan siparişleri görsün
        queryset = super().get_queryset().order_by('-order_date')
        if self.request.user.is_personnel() and not self.request.user.is_admin():
            queryset = queryset.exclude(order_status='passive')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Sipariş Listesi'
        return context


class OrderDetailView(PersonnelRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_personnel() and not self.request.user.is_admin():
            queryset = queryset.exclude(order_status='passive')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Sipariş Detayı: {self.object.order_id}"
        return context


class OrderCreateView(PersonnelRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = OrderItemFormSet(self.request.POST)
        else:
            data['items'] = OrderItemFormSet()
        data['page_title'] = 'Yeni Sipariş Oluştur'
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items']
        
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.save() # Siparişi önce kaydet ki ID'si oluşsun

            if items_formset.is_valid():
                total_order_price_from_items = 0
                has_valid_items = False
                for item_form in items_formset:
                    if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                        has_valid_items = True
                        order_item = item_form.save(commit=False)
                        order_item.order = self.object
                        
                        product = order_item.product
                        order_item.unit_price = product.discounted_price
                        
                        if product.current_stock < order_item.quantity:
                            messages.error(self.request, f"'{product.name}' ürünü için yeterli stok yok. Mevcut: {product.current_stock} adet. Sipariş kalemi güncellenemedi.")
                            transaction.set_rollback(True) # Hata olursa işlemi geri al
                            return self.form_invalid(form) # Formu geçersiz say
                        
                        product.current_stock -= order_item.quantity
                        product.save()
                        
                        order_item.save()
                        total_order_price_from_items += order_item.total_price
                
                if not has_valid_items:
                    messages.error(self.request, "Sipariş en az bir ürün içermelidir.")
                    transaction.set_rollback(True)
                    return self.form_invalid(form)

                self.object.total_amount = total_order_price_from_items - self.object.discount_amount
                if self.object.total_amount < 0:
                    self.object.total_amount = 0
                self.object.save()
                
            else:
                messages.error(self.request, "Sipariş kalemlerinde hata var. Lütfen kontrol edin.")
                transaction.set_rollback(True)
                return self.form_invalid(form)

        messages.success(self.request, f"Sipariş {self.object.order_id} başarıyla oluşturuldu.")
        if self.object.customer:
            create_notification(self.object.customer, f"Yeni siparişiniz ({self.object.order_id}) oluşturuldu.", 'order_status', self.object)
        for staff_user in User.objects.filter(user_type__in=['admin', 'personnel']):
            create_notification(staff_user, f"Yeni bir sipariş oluşturuldu: {self.object.order_id}", 'system_alert', self.object)

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Sipariş oluşturulurken bir hata oluştu. Lütfen bilgileri kontrol edin.")
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class OrderUpdateView(PersonnelRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = OrderItemFormSet(self.request.POST, instance=self.object)
        else:
            data['items'] = OrderItemFormSet(instance=self.object)
        data['page_title'] = f"Sipariş Düzenle: {self.object.order_id}"
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items']
        
        with transaction.atomic():
            old_order_items = {item.pk: item.quantity for item in self.object.items.all()}

            self.object = form.save(commit=False)
            self.object.save()

            if items_formset.is_valid():
                total_order_price_from_items = 0
                has_valid_items = False
                
                # Stokları eski hallerine geri getir (güncelleme öncesi durumu için)
                for item_pk, old_quantity in old_order_items.items():
                    try:
                        order_item_instance = OrderItem.objects.get(pk=item_pk)
                        product_to_restore = order_item_instance.product
                        if product_to_restore:
                            product_to_restore.current_stock += old_quantity
                            product_to_restore.save()
                    except OrderItem.DoesNotExist:
                        pass

                # Formset'teki item'ları işle
                for item_form in items_formset:
                    if item_form.cleaned_data:
                        if item_form.cleaned_data.get('DELETE'):
                            if item_form.instance.pk:
                                item_form.instance.delete()
                        else:
                            has_valid_items = True
                            order_item = item_form.save(commit=False)
                            order_item.order = self.object
                            product = order_item.product

                            # Stok kontrolü
                            if product.current_stock < order_item.quantity:
                                messages.error(self.request, f"'{product.name}' ürünü için yeterli stok bulunmamaktadır. Mevcut: {product.current_stock} adet. Sipariş kalemi güncellenemedi.")
                                transaction.set_rollback(True)
                                return self.form_invalid(form)
                            
                            product.current_stock -= order_item.quantity
                            product.save()
                            
                            order_item.unit_price = product.discounted_price
                            order_item.save()
                            total_order_price_from_items += order_item.total_price

                if not has_valid_items:
                    messages.error(self.request, "Sipariş en az bir ürün içermelidir.")
                    transaction.set_rollback(True)
                    return self.form_invalid(form)

                self.object.total_amount = total_order_price_from_items - self.object.discount_amount
                if self.object.total_amount < 0:
                    self.object.total_amount = 0
                self.object.save()

            else:
                messages.error(self.request, "Sipariş kalemlerinde hata var. Lütfen kontrol edin.")
                transaction.set_rollback(True)
                return self.form_invalid(form)

        messages.success(self.request, f"Sipariş {self.object.order_id} başarıyla güncellendi.")
        if self.object.customer:
            create_notification(self.object.customer, f"Siparişiniz ({self.object.order_id}) güncellendi.", 'order_status', self.object)
        for staff_user in User.objects.filter(user_type__in=['admin', 'personnel']):
            create_notification(staff_user, f"Sipariş {self.object.order_id} güncellendi.", 'system_alert', self.object)

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Sipariş güncellenirken bir hata oluştu. Lütfen bilgileri kontrol edin.")
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class OrderDeleteView(PersonnelRequiredMixin, DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:order_list')

    def form_valid(self, form):
        with transaction.atomic():
            for item in self.object.items.all():
                product = item.product
                if product:
                    product.current_stock += item.quantity
                    product.save()
            messages.success(self.request, f"Sipariş {self.object.order_id} başarıyla silindi ve ürünler stoğa geri eklendi.")
            if self.object.customer:
                create_notification(self.object.customer, f"Siparişiniz ({self.object.order_id}) silindi.", 'order_status', self.object)
            for staff_user in User.objects.filter(user_type__in=['admin', 'personnel']):
                create_notification(staff_user, f"Sipariş {self.object.order_id} silindi.", 'system_alert', self.object)

            return super().form_valid(form)

def order_accept(request, pk):
    if not request.user.is_authenticated or not (request.user.is_personnel() or request.user.is_admin()):
        messages.error(request, "Bu işlemi gerçekleştirmek için yetkiniz yok.")
        return redirect('home')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        if order.order_status == 'new':
            order.order_status = 'accepted'
            order.save()
            messages.success(request, f"Sipariş {order.order_id} kabul edildi ve hazırlanıyor olarak işaretlendi.")
            if order.customer:
                create_notification(order.customer, f"Siparişiniz ({order.order_id}) kabul edildi ve hazırlanıyor.", 'order_status', order)
            for staff_user in User.objects.filter(user_type__in=['admin', 'personnel']):
                create_notification(staff_user, f"Sipariş {order.order_id} kabul edildi.", 'system_alert', order)
        else:
            messages.warning(request, f"Sipariş {order.order_id} zaten {order.get_order_status_display()} durumunda.")
        return redirect('orders:order_detail', pk=pk)
    
    messages.info(request, "Siparişi kabul etmek için POST isteği gönderin.")
    return redirect('orders:order_detail', pk=pk)

def order_mark_shipped(request, pk):
    if not request.user.is_authenticated or not (request.user.is_personnel() or request.user.is_admin()):
        messages.error(request, "Bu işlemi gerçekleştirmek için yetkiniz yok.")
        return redirect('home')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        if order.order_status in ['accepted', 'new']:
            order.order_status = 'shipped'
            order.save()
            messages.success(request, f"Sipariş {order.order_id} kargoya verildi olarak işaretlendi.")
            if order.customer:
                create_notification(order.customer, f"Siparişiniz ({order.order_id}) kargoya verildi. Takip No: {order.tracking_number if order.tracking_number else 'Belirtilmemiş'}", 'order_status', order)
            for staff_user in User.objects.filter(user_type__in=['admin', 'personnel']):
                create_notification(staff_user, f"Sipariş {order.order_id} kargoya verildi.", 'system_alert', order)
        else:
            messages.warning(request, f"Sipariş {order.order_id} zaten {order.get_order_status_display()} durumunda.")
        return redirect('orders:order_detail', pk=pk)
    messages.info(request, "Siparişi kargoya vermek için POST isteği gönderin.")
    return redirect('orders:order_detail', pk=pk)

def order_mark_delivered(request, pk):
    if not request.user.is_authenticated or not (request.user.is_personnel() or request.user.is_admin()):
        messages.error(request, "Bu işlemi gerçekleştirmek için yetkiniz yok.")
        return redirect('home')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        if order.order_status in ['shipped', 'accepted', 'new']:
            order.order_status = 'delivered'
            order.is_completed = True
            order.save()
            messages.success(request, f"Sipariş {order.order_id} başarıyla teslim edildi ve tamamlandı olarak işaretlendi.")
            if order.customer:
                create_notification(order.customer, f"Siparişiniz ({order.order_id}) başarıyla teslim edildi. Yeni siparişinizde görüşmek üzere:)", 'order_status', order)
            for staff_user in User.objects.filter(user_type__in=['admin', 'personnel']):
                create_notification(staff_user, f"Sipariş {order.order_id} teslim edildi.", 'system_alert', order)
        else:
            messages.warning(request, f"Sipariş {order.order_id} zaten {order.get_order_status_display()} durumunda.")
        return redirect('orders:order_detail', pk=pk)
    messages.info(request, "Siparişi teslim edildi olarak işaretlemek için POST isteği gönderin.")
    return redirect('orders:order_detail', pk=pk)

def order_mark_cancelled(request, pk):
    if not request.user.is_authenticated or not (request.user.is_personnel() or request.user.is_admin()):
        messages.error(request, "Bu işlemi gerçekleştirmek için yetkiniz yok.")
        return redirect('home')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        if order.order_status not in ['delivered', 'returned', 'cancelled', 'passive']:
            with transaction.atomic():
                order.order_status = 'cancelled'
                order.is_completed = True
                order.save()
                
                for item in order.items.all():
                    product = item.product
                    if product:
                        product.current_stock += item.quantity
                        product.save()
                messages.success(request, f"Sipariş {order.order_id} başarıyla iptal edildi ve ürünler stoğa geri eklendi.")
                if order.customer:
                    create_notification(order.customer, f"Siparişiniz ({order.order_id}) iptal edildi.", 'order_status', order)
                for staff_user in User.objects.filter(user_type__in=['admin', 'personnel']):
                    create_notification(staff_user, f"Sipariş {order.order_id} iptal edildi.", 'system_alert', order)
        else:
            messages.warning(request, f"Sipariş {order.order_id} zaten {order.get_order_status_display()} durumunda.")
        return redirect('orders:order_detail', pk=pk)
    messages.info(request, "Siparişi iptal etmek için POST isteği gönderin.")
    return redirect('orders:order_detail', pk=pk)

def order_mark_returned(request, pk):
    if not request.user.is_authenticated or not (request.user.is_personnel() or request.user.is_admin()):
        messages.error(request, "Bu işlemi gerçekleştirmek için yetkiniz yok.")
        return redirect('home')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        if order.order_status in ['delivered', 'shipped']:
            with transaction.atomic():
                order.order_status = 'returned'
                order.is_completed = True
                order.save()
                
                for item in order.items.all():
                    product = item.product
                    if product:
                        product.current_stock += item.quantity
                        product.save()
                messages.success(request, f"Sipariş {order.order_id} başarıyla iade edildi ve ürünler stoğa geri eklendi.")
                if order.customer:
                    create_notification(order.customer, f"Siparişiniz ({order.order_id}) iade edildi.", 'order_status', order)
                for staff_user in User.objects.filter(user_type__in=['admin', 'personnel']):
                    create_notification(staff_user, f"Sipariş {order.order_id} iade edildi.", 'system_alert', order)
        else:
            messages.warning(request, f"Sipariş {order.order_id} {order.get_order_status_display()} durumunda, iade edilemez.")
        return redirect('orders:order_detail', pk=pk)
    messages.info(request, "Siparişi iade etmek için POST isteği gönderin.")
    return redirect('orders:order_detail', pk=pk)

def order_mark_passive(request, pk):
    if not request.user.is_authenticated or not request.user.is_admin(): # Sadece Admin pasife alabilir
        messages.error(request, "Bu işlemi gerçekleştirmek için yetkiniz yok.")
        return redirect('home')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        if order.order_status != 'passive':
            order.order_status = 'passive'
            order.save()
            messages.success(request, f"Sipariş {order.order_id} pasif olarak işaretlendi.")
        else:
            messages.warning(request, f"Sipariş {order.order_id} zaten pasif durumda.")
        return redirect('orders:order_list')
    messages.info(request, "Siparişi pasife almak için POST isteği gönderin.")
    return redirect('orders:order_detail', pk=pk)