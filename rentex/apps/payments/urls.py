from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<uuid:booking_pk>/', views.payment_initiate, name='checkout'),
    path('success/<uuid:booking_pk>/', views.payment_success, name='success'),
    path('history/', views.payment_history, name='history'),
    path('webhook/razorpay/', views.razorpay_webhook, name='razorpay_webhook'),
    path('demo-complete/<uuid:booking_pk>/', views.demo_payment_complete, name='demo_complete'),
]
