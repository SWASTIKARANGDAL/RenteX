from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<uuid:booking_pk>/', views.create_review, name='create'),
    path('<int:pk>/delete/', views.delete_review, name='delete'),
    path('product/<slug:slug>/', views.product_reviews, name='product_reviews'),
]
