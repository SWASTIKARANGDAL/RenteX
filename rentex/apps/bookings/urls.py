from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='list'),
    path('create/<slug:slug>/', views.create_booking, name='create'),
    path('<uuid:pk>/', views.booking_detail, name='detail'),
    path('<uuid:pk>/confirm/', views.confirm_booking, name='confirm'),
    path('<uuid:pk>/reject/', views.reject_booking, name='reject'),
    path('<uuid:pk>/cancel/', views.cancel_booking, name='cancel'),
    path('<uuid:pk>/complete/', views.complete_booking, name='complete'),
    path('<uuid:pk>/invoice/', views.generate_invoice, name='invoice'),
    path('calculate-price/', views.calculate_price, name='calculate_price'),
]
