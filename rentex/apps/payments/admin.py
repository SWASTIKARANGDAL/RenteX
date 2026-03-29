from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'gateway', 'amount', 'currency', 'status', 'paid_at', 'created_at']
    list_filter = ['gateway', 'status', 'currency']
    search_fields = ['booking__booking_number', 'gateway_payment_id', 'gateway_order_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
