from django.contrib import admin
from .models import Category, Brand, Firm, Product, Purchases, Sales

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_products')
    search_fields = ('name',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Firm)
class FirmAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created')
    search_fields = ('name', 'phone')
    list_filter = ('created',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'stock', 'created')
    list_filter = ('category', 'brand', 'created')
    search_fields = ('name', 'category__name', 'brand__name')
    readonly_fields = ('stock',)

@admin.register(Purchases)
class PurchasesAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'price', 'price_total', 'firm', 'created')
    list_filter = ('product', 'firm', 'created')
    search_fields = ('product__name', 'firm__name')
    readonly_fields = ('price_total',)

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'price', 'price_total', 'created')
    list_filter = ('product', 'brand', 'created')
    search_fields = ('product__name', 'brand__name')
    readonly_fields = ('price_total',)
