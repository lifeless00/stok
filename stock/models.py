from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    @property
    def total_products(self):
        return self.products.count()
    
    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'

class Brand(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='brands/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Marka'
        verbose_name_plural = 'Markalar'

class Firm(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Firma'
        verbose_name_plural = 'Firmalar'

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.brand.name}"
    
    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'

class Purchases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    @property
    def price_total(self):
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Yeni kayıt
            self.product.stock += self.quantity
            self.product.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Alım'
        verbose_name_plural = 'Alımlar'

class Sales(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.price_total = self.quantity * self.price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} adet"
    
    class Meta:
        verbose_name = 'Satış'
        verbose_name_plural = 'Satışlar'
        ordering = ['-created']
