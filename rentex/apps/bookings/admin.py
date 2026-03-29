from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_number', 'renter', 'product', 'status', 'start_date', 'end_date', 'total_amount', 'created_at']
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['booking_number', 'renter__email', 'product__name']
    readonly_fields = ['id', 'booking_number', 'created_at', 'updated_at', 'confirmed_at', 'completed_at']
    date_hierarchy = 'created_at'
    list_editable = ['status']

    actions = ['confirm_bookings', 'complete_bookings']

    def confirm_bookings(self, request, queryset):
        queryset.filter(status='pending').update(status='confirmed')
    confirm_bookings.short_description = "Confirm selected bookings"

    def complete_bookings(self, request, queryset):
        queryset.filter(status='confirmed').update(status='completed')
    complete_bookings.short_description = "Mark selected as completed"
