from django.contrib import admin
from .models import Category, Product, ProductImage, ProductSpecification, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count', 'order']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2


class ProductSpecInline(admin.TabularInline):
    model = ProductSpecification
    extra = 2


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'category', 'price_per_day', 'city', 'is_available', 'is_featured', 'created_at']
    list_filter = ['category', 'condition', 'is_available', 'is_featured', 'state']
    search_fields = ['name', 'description', 'owner__email', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_available', 'is_featured']
    inlines = [ProductImageInline, ProductSpecInline]
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
