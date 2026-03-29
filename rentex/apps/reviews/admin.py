from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'product', 'rating', 'review_type', 'is_approved', 'created_at']
    list_filter = ['review_type', 'rating', 'is_approved']
    search_fields = ['reviewer__email', 'product__name', 'comment']
    list_editable = ['is_approved']
    date_hierarchy = 'created_at'
