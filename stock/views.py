# stock/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

# Proje içi importlar
from core.views import PersonnelRequiredMixin
from .models import Category, Supplier, Warehouse, Product
from .forms import CategoryForm, SupplierForm, WarehouseForm, ProductForm


# --- Kategori Yönetimi (CRUD) ---
class CategoryListView(PersonnelRequiredMixin, ListView):
    model = Category
    template_name = 'stock/category_list.html'
    context_object_name = 'categories'
    paginate_by = 15

class CategoryCreateView(PersonnelRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'stock/category_form.html'  # <<<<< DEĞİŞTİRİLDİ
    success_url = reverse_lazy('stock:category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Yeni Kategori Ekle"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Kategori başarıyla eklendi.")
        return super().form_valid(form)

class CategoryUpdateView(PersonnelRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'stock/category_form.html'  # <<<<< DEĞİŞTİRİLDİ
    success_url = reverse_lazy('stock:category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Kategoriyi Düzenle"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Kategori başarıyla güncellendi.")
        return super().form_valid(form)

class CategoryDeleteView(PersonnelRequiredMixin, DeleteView):
    model = Category
    template_name = 'stock/generic_confirm_delete.html'
    success_url = reverse_lazy('stock:category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Kategoriyi Sil"
        context['message'] = f"'{self.object.name}' adlı kategoriyi silmek istediğinizden emin misiniz?"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"'{self.object.name}' kategorisi başarıyla silindi.")
        return super().form_valid(form)


# --- Tedarikçi Yönetimi (CRUD) ---
class SupplierListView(PersonnelRequiredMixin, ListView):
    model = Supplier
    template_name = 'stock/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 15

class SupplierCreateView(PersonnelRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'stock/supplier_form.html'  # <<<<< DEĞİŞTİRİLDİ
    success_url = reverse_lazy('stock:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Yeni Tedarikçi Ekle"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Tedarikçi başarıyla eklendi.")
        return super().form_valid(form)

class SupplierUpdateView(PersonnelRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'stock/supplier_form.html'  # <<<<< BURASI ZATEN DOĞRUYDU, KORUNDU
    success_url = reverse_lazy('stock:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Tedarikçiyi Düzenle"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Tedarikçi başarıyla güncellendi.")
        return super().form_valid(form)

class SupplierDeleteView(PersonnelRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'stock/generic_confirm_delete.html'
    success_url = reverse_lazy('stock:supplier_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Tedarikçiyi Sil"
        context['message'] = f"'{self.object.name}' adlı tedarikçiyi silmek istediğinizden emin misiniz?"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"'{self.object.name}' tedarikçisi başarıyla silindi.")
        return super().form_valid(form)


# --- Depo Yönetimi (CRUD) ---
class WarehouseListView(PersonnelRequiredMixin, ListView):
    model = Warehouse
    template_name = 'stock/warehouse_list.html'
    context_object_name = 'warehouses'
    paginate_by = 15

class WarehouseCreateView(PersonnelRequiredMixin, CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'stock/warehouse_form.html'  # <<<<< DEĞİŞTİRİLDİ
    success_url = reverse_lazy('stock:warehouse_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Yeni Depo Ekle"
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Depo başarıyla eklendi.")
        return super().form_valid(form)

class WarehouseUpdateView(PersonnelRequiredMixin, UpdateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'stock/warehouse_form.html'  # <<<<< DEĞİŞTİRİLDİ
    success_url = reverse_lazy('stock:warehouse_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Depoyu Düzenle"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Depo başarıyla güncellendi.")
        return super().form_valid(form)

class WarehouseDeleteView(PersonnelRequiredMixin, DeleteView):
    model = Warehouse
    template_name = 'stock/generic_confirm_delete.html'
    success_url = reverse_lazy('stock:warehouse_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Depoyu Sil"
        context['message'] = f"'{self.object.name}' adlı depoyu silmek istediğinizden emin misiniz?"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"'{self.object.name}' deposu başarıyla silindi.")
        return super().form_valid(form)


# --- Ürün Yönetimi ---
class ProductListView(PersonnelRequiredMixin, ListView):
    model = Product
    template_name = 'stock/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category', 'main_supplier').order_by('name')
        status = self.request.GET.get('status', 'all')

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status_filter'] = self.request.GET.get('status', 'all')
        return context

class ProductDetailView(PersonnelRequiredMixin, DetailView):
    model = Product
    template_name = 'stock/product_detail.html'
    context_object_name = 'product'

class ProductCreateView(PersonnelRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'stock/product_form.html' # Bu zaten doğruydu
    success_url = reverse_lazy('stock:product_list')

    def form_valid(self, form):
        messages.success(self.request, "Ürün başarıyla eklendi.")
        return super().form_valid(form)

class ProductUpdateView(PersonnelRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'stock/product_form.html' # Bu zaten doğruydu
    success_url = reverse_lazy('stock:product_list')

    def form_valid(self, form):
        messages.success(self.request, "Ürün başarıyla güncellendi.")
        return super().form_valid(form)

class ProductDeleteView(PersonnelRequiredMixin, DeleteView):
    model = Product
    template_name = 'stock/generic_confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Ürünü Sil"
        context['message'] = f"'{self.object.name}' adlı ürünü kalıcı olarak silmek istediğinizden emin misiniz? Bu işlem geri alınamaz."
        return context

    def form_valid(self, form):
        messages.success(self.request, f"'{self.object.name}' ürünü başarıyla silindi.")
        return super().form_valid(form)

def is_personnel_or_admin(user):
    return user.is_authenticated and (user.is_personnel() or user.is_admin())

@user_passes_test(is_personnel_or_admin)
def product_deactivate(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.warning(request, f"'{product.name}' ürünü başarıyla pasife alındı.")
    return redirect('stock:product_list')

@user_passes_test(is_personnel_or_admin)
def product_activate(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.is_active = True
        product.save()
        messages.success(request, f"'{product.name}' ürünü başarıyla aktife alındı.")
    return redirect('stock:product_list')