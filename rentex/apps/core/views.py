from django.shortcuts import render
from django.db.models import Count, Avg
from apps.products.models import Product, Category
from apps.accounts.models import User


def home(request):
    featured = Product.objects.filter(is_available=True, is_featured=True).select_related('owner', 'category').prefetch_related('images')[:8]
    latest = Product.objects.filter(is_available=True).select_related('owner', 'category').prefetch_related('images').order_by('-created_at')[:8]
    categories = Category.objects.annotate(count=Count('products')).filter(count__gt=0).order_by('order')[:8]
    total_products = Product.objects.filter(is_available=True).count()
    total_owners = User.objects.filter(role='owner').count()
    total_renters = User.objects.filter(role='renter').count()

    context = {
        'featured_products': featured,
        'latest_products': latest,
        'categories': categories,
        'stats': {
            'products': total_products,
            'owners': total_owners,
            'renters': total_renters,
            'cities': Product.objects.values('city').distinct().count(),
        }
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def how_it_works(request):
    return render(request, 'core/how_it_works.html')


def contact(request):
    return render(request, 'core/contact.html')
