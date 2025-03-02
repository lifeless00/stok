from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Brand, Firm, Product, Purchases, Sales
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.contrib import messages
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer,
    PurchasesSerializer, SalesSerializer, FirmSerializer
)
from django.http import JsonResponse
from django.contrib.auth import logout
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
import uuid
from django.db.models import F
import logging

logger = logging.getLogger(__name__)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategorySerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class FirmViewSet(viewsets.ModelViewSet):
    queryset = Firm.objects.all()
    serializer_class = FirmSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['category', 'brand']

class PurchasesViewSet(viewsets.ModelViewSet):
    queryset = Purchases.objects.all()
    serializer_class = PurchasesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['firm__name']
    filterset_fields = ['firm', 'product']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SalesViewSet(viewsets.ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['brand__name']
    filterset_fields = ['brand', 'product']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@login_required
def index(request):
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_purchases': Purchases.objects.count(),
        'total_sales': Sales.objects.count(),
        'recent_purchases': Purchases.objects.order_by('-created')[:5],
        'recent_sales': Sales.objects.order_by('-created')[:5],
    }
    return render(request, 'stock/index.html', context)

@login_required
def category_list(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            messages.success(request, 'Kategori başarıyla eklendi.')
            return redirect('category_list')
        else:
            messages.error(request, 'Kategori adı boş olamaz!')
    
    categories = Category.objects.all()
    return render(request, 'stock/category_list.html', {'categories': categories})

@login_required
def product_list(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        image = request.FILES.get('image')
        
        if name and category_id and brand_id:
            try:
                category = Category.objects.get(id=category_id)
                brand = Brand.objects.get(id=brand_id)
                
                product = Product.objects.create(
                    name=name,
                    category=category,
                    brand=brand
                )
                if image:
                    product.image = image
                    product.save()
                    
                messages.success(request, 'Ürün başarıyla eklendi.')
                return redirect('product_list')
            except (Category.DoesNotExist, Brand.DoesNotExist):
                messages.error(request, 'Geçersiz kategori veya marka seçimi!')
        else:
            messages.error(request, 'Tüm alanları doldurun!')
    
    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'stock/product_list.html', {
        'products': products,
        'categories': categories,
        'brands': brands
    })

@login_required
def purchase_list(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        firm_id = request.POST.get('firm')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        
        if product_id and firm_id and quantity and price:
            try:
                product = Product.objects.get(id=product_id)
                firm = Firm.objects.get(id=firm_id)
                quantity = int(quantity)
                price = float(price)
                
                if quantity > 0 and price > 0:
                    Purchases.objects.create(
                        user=request.user,
                        product=product,
                        firm=firm,
                        quantity=quantity,
                        price=price
                    )
                    messages.success(request, 'Alım başarıyla kaydedildi.')
                    return redirect('purchase_list')
                else:
                    messages.error(request, 'Miktar ve fiyat 0\'dan büyük olmalı!')
            except (Product.DoesNotExist, Firm.DoesNotExist):
                messages.error(request, 'Geçersiz ürün veya firma seçimi!')
            except ValueError:
                messages.error(request, 'Geçersiz miktar veya fiyat!')
        else:
            messages.error(request, 'Tüm alanları doldurun!')
    
    purchases = Purchases.objects.all().order_by('-created')
    products = Product.objects.all()
    firms = Firm.objects.all()
    return render(request, 'stock/purchase_list.html', {
        'purchases': purchases,
        'products': products,
        'firms': firms
    })

@login_required
def sale_list(request):
    sales = Sales.objects.all().order_by('-created')
    context = {
        'sales': sales
    }
    return render(request, 'stock/sale_list.html', context)

@login_required
def brand_list(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        
        if name:
            brand = Brand.objects.create(name=name)
            if image:
                brand.image = image
                brand.save()
            messages.success(request, 'Marka başarıyla eklendi.')
            return redirect('brand_list')
        else:
            messages.error(request, 'Marka adı boş olamaz!')
    
    brands = Brand.objects.all()
    return render(request, 'stock/brand_list.html', {'brands': brands})

@login_required
def firm_list(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        if name and phone and address:
            Firm.objects.create(
                name=name,
                phone=phone,
                address=address
            )
            messages.success(request, 'Firma başarıyla eklendi.')
            return redirect('firm_list')
        else:
            messages.error(request, 'Tüm alanları doldurun!')
    
    firms = Firm.objects.all()
    return render(request, 'stock/firm_list.html', {'firms': firms})

# Süper kullanıcı kontrolü için fonksiyon
def is_superuser(user):
    return user.is_superuser

# Sadece süper kullanıcıların erişebileceği viewler
@login_required
@user_passes_test(is_superuser)
def edit_category(request, pk):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category = get_object_or_404(Category, pk=pk)
            category.name = name
            category.save()
            messages.success(request, 'Kategori güncellendi.')
        else:
            messages.error(request, 'Kategori adı boş olamaz!')
    return redirect('category_list')

@login_required
@user_passes_test(is_superuser)
def edit_brand(request, pk):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        
        if name:
            brand = get_object_or_404(Brand, pk=pk)
            brand.name = name
            if image:
                brand.image = image
            brand.save()
            messages.success(request, 'Marka güncellendi.')
        else:
            messages.error(request, 'Marka adı boş olamaz!')
    return redirect('brand_list')

@login_required
@user_passes_test(is_superuser)
def edit_firm(request, pk):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        if name and phone and address:
            firm = get_object_or_404(Firm, pk=pk)
            firm.name = name
            firm.phone = phone
            firm.address = address
            firm.save()
            messages.success(request, 'Firma güncellendi.')
        else:
            messages.error(request, 'Tüm alanları doldurun!')
    return redirect('firm_list')

@login_required
@user_passes_test(is_superuser)
def edit_product(request, pk):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        image = request.FILES.get('image')
        
        if name and category_id and brand_id:
            try:
                product = get_object_or_404(Product, pk=pk)
                category = Category.objects.get(id=category_id)
                brand = Brand.objects.get(id=brand_id)
                
                product.name = name
                product.category = category
                product.brand = brand
                if image:
                    product.image = image
                product.save()
                messages.success(request, 'Ürün güncellendi.')
            except (Category.DoesNotExist, Brand.DoesNotExist):
                messages.error(request, 'Geçersiz kategori veya marka seçimi!')
        else:
            messages.error(request, 'Tüm alanları doldurun!')
    return redirect('product_list')

@login_required
@user_passes_test(is_superuser)
def add_stock(request, product_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        if quantity:
            try:
                product = get_object_or_404(Product, id=product_id)
                quantity = int(quantity)
                if quantity > 0:
                    product.stock += quantity
                    product.save()
                    messages.success(request, f'{quantity} adet stok eklendi.')
                else:
                    messages.error(request, 'Geçerli bir miktar girin!')
            except ValueError:
                messages.error(request, 'Geçerli bir sayı girin!')
        else:
            messages.error(request, 'Miktar boş olamaz!')
    return redirect('product_list')

@login_required
@user_passes_test(is_superuser)
def remove_stock(request, product_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        if quantity:
            try:
                product = get_object_or_404(Product, id=product_id)
                quantity = int(quantity)
                if quantity > 0:
                    if product.stock >= quantity:
                        product.stock -= quantity
                        product.save()
                        messages.success(request, f'{quantity} adet stok çıkarıldı.')
                    else:
                        messages.error(request, 'Yetersiz stok!')
                else:
                    messages.error(request, 'Geçerli bir miktar girin!')
            except ValueError:
                messages.error(request, 'Geçerli bir sayı girin!')
        else:
            messages.error(request, 'Miktar boş olamaz!')
    return redirect('product_list')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def sale_page(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        
        logger.info(f"[SATIŞ BAŞLANGIÇ] POST isteği alındı - product_id: {product_id}, quantity: {quantity}, price: {price}")
        
        if product_id and quantity and price:
            try:
                with transaction.atomic():
                    product = Product.objects.select_for_update().get(id=product_id)
                    quantity = int(quantity)
                    price = float(price)
                    
                    logger.info(f"[STOK KONTROL] Ürün ID: {product_id}, Mevcut stok: {product.stock}")
                    
                    if quantity <= 0 or price <= 0:
                        messages.error(request, 'Miktar ve fiyat 0\'dan büyük olmalı!')
                        return redirect('sale_page')
                    
                    if product.stock < quantity:
                        messages.error(request, 'Yetersiz stok!')
                        return redirect('sale_page')
                    
                    # Satış kaydı oluştur
                    sale = Sales.objects.create(
                        user=request.user,
                        product=product,
                        brand=product.brand,
                        quantity=quantity,
                        price=price,
                        price_total=quantity * price
                    )
                    
                    logger.info(f"[SATIŞ KAYDI] Satış ID: {sale.id} oluşturuldu")
                    
                    # Stok güncelle
                    old_stock = product.stock
                    product.stock = product.stock - quantity
                    product.save()
                    
                    logger.info(f"[STOK GÜNCELLEME] Eski stok: {old_stock}, Yeni stok: {product.stock}")
                    
                    messages.success(request, 'Satış başarıyla kaydedildi.')
                    
                    logger.info(f"[SATIŞ TAMAMLANDI] İşlem başarılı")
                    
                return redirect('sale_page')
                    
            except Product.DoesNotExist:
                logger.error(f"[HATA] Ürün bulunamadı - ID: {product_id}")
                messages.error(request, 'Ürün bulunamadı!')
            except ValueError as e:
                logger.error(f"[HATA] Değer hatası - {str(e)}")
                messages.error(request, 'Geçersiz miktar veya fiyat!')
            except Exception as e:
                logger.error(f"[HATA] Beklenmeyen hata - {str(e)}")
                messages.error(request, f'Bir hata oluştu: {str(e)}')
        else:
            logger.warning("[HATA] Eksik veri")
            messages.error(request, 'Tüm alanları doldurun!')

    products = Product.objects.all().order_by('name')
    return render(request, 'stock/sale_page.html', {'products': products}) 
