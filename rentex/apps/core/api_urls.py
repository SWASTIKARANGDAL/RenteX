from django.urls import path
from apps.products import views as product_views
from apps.bookings import views as booking_views

urlpatterns = [
    path('check-availability/<slug:slug>/', product_views.check_availability, name='api_availability'),
    path('calculate-price/', booking_views.calculate_price, name='api_calculate_price'),
    path('wishlist/<slug:slug>/', product_views.toggle_wishlist, name='api_toggle_wishlist'),
    path('notifications/unread/', __import__('apps.notifications.views', fromlist=['unread_count']).unread_count, name='api_unread_count'),
    path('notifications/mark-all-read/', __import__('apps.notifications.views', fromlist=['mark_all_read']).mark_all_read, name='api_mark_all_read'),
]
