from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('create/', views.product_create, name='create'),
    path('my/', views.my_products, name='my_products'),
    path('wishlist/', views.my_wishlist, name='wishlist'),
    path('category/<slug:slug>/', views.category_products, name='by_category'),
    path('<slug:slug>/', views.product_detail, name='detail'),
    path('<slug:slug>/edit/', views.product_edit, name='edit'),
    path('<slug:slug>/delete/', views.product_delete, name='delete'),
    path('<slug:slug>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('<slug:slug>/availability/', views.check_availability, name='check_availability'),
]
