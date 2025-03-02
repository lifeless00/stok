from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'purchases', views.PurchasesViewSet)
router.register(r'sales', views.SalesViewSet)
router.register(r'firms', views.FirmViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.category_list, name='category_list'),
    path('brands/', views.brand_list, name='brand_list'),
    path('firms/', views.firm_list, name='firm_list'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/add-stock/', views.add_stock, name='add_stock'),
    path('products/<int:product_id>/remove-stock/', views.remove_stock, name='remove_stock'),
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('sales/', views.sale_list, name='sale_list'),
    path('logout/', views.logout_view, name='logout'),
    path('api/', include(router.urls)),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('brands/<int:pk>/edit/', views.edit_brand, name='edit_brand'),
    path('firms/<int:pk>/edit/', views.edit_firm, name='edit_firm'),
    path('sales/page/', views.sale_page, name='sale_page'),
] 