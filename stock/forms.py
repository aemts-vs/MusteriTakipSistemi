# stock/forms.py
from django import forms
from .models import Category, Supplier, Warehouse, Product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Kategori Adı',
            'description': 'Açıklama',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'address', 'phone_number', 'email', 'contact_person', 'notes']
        labels = {
            'name': 'Firma Adı',
            'address': 'Adres',
            'phone_number': 'Telefon Numarası',
            'email': 'E-posta Adresi',
            'contact_person': 'İlgili Kişi',
            'notes': 'Notlar',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'address', 'description']
        labels = {
            'name': 'Depo Adı',
            'address': 'Depo Adresi',
            'description': 'Açıklama',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_code', 'name', 'category', 'current_stock',
            'minimum_stock', 'warehouse_location', 'unit_cost',
            'selling_price', 'main_supplier', 'image', 'description', 'is_active'
        ]
        labels = {
            'product_code': 'Ürün Kodu',
            'name': 'Ürün Adı',
            'category': 'Kategori',
            'current_stock': 'Mevcut Stok',
            'minimum_stock': 'Minimum Stok',
            'warehouse_location': 'Depo Konumu',
            'unit_cost': 'Birim Maliyet (TL)',
            'selling_price': 'Satış Fiyatı (TL)',
            'main_supplier': 'Ana Tedarikçi',
            'image': 'Ürün Görseli',
            'description': 'Ürün Açıklaması',
            'is_active': 'Aktif Ürün',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }