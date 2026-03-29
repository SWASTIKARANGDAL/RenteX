from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from .models import Product, Category, ProductImage, Wishlist
from .forms import ProductForm, ProductImageFormSet, ProductSearchForm


def product_list(request):
    form = ProductSearchForm(request.GET)
    products = Product.objects.filter(is_available=True).select_related('owner', 'category').prefetch_related('images')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        city = form.cleaned_data.get('city')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        condition = form.cleaned_data.get('condition')
        sort = form.cleaned_data.get('sort') or '-created_at'

        if q:
            products = products.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(brand__icontains=q))
        if category:
            products = products.filter(category=category)
        if city:
            products = products.filter(city__icontains=city)
        if min_price:
            products = products.filter(price_per_day__gte=min_price)
        if max_price:
            products = products.filter(price_per_day__lte=max_price)
        if condition:
            products = products.filter(condition=condition)
        products = products.order_by(sort)

    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)
    categories = Category.objects.annotate(count=Count('products')).filter(count__gt=0)

    return render(request, 'products/list.html', {
        'products': products_page,
        'form': form,
        'categories': categories,
        'total_count': paginator.count,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    product.views_count += 1
    product.save(update_fields=['views_count'])

    related = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(id=product.id)[:4]

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'related': related,
        'in_wishlist': in_wishlist,
        'images': product.images.all(),
        'specs': product.specifications.all(),
        'reviews': product.reviews.select_related('reviewer').order_by('-created_at'),
    }
    return render(request, 'products/detail.html', context)


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True).select_related('owner').prefetch_related('images')
    paginator = Paginator(products, 12)
    products_page = paginator.get_page(request.GET.get('page'))
    return render(request, 'products/category.html', {
        'category': category,
        'products': products_page,
    })


@login_required
def my_products(request):
    if not request.user.is_owner:
        messages.error(request, 'Only owners can manage products.')
        return redirect('accounts:dashboard')
    products = Product.objects.filter(owner=request.user).annotate(
        booking_count=Count('bookings'),
        avg_rating_calc=Avg('reviews__rating')
    )
    return render(request, 'products/my_products.html', {'products': products})


@login_required
def product_create(request):
    if not request.user.is_owner:
        messages.error(request, 'Only owners can add products.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            formset.instance = product
            images = formset.save(commit=False)
            for i, image in enumerate(images):
                if not ProductImage.objects.filter(product=product).exists():
                    image.is_primary = True
                image.order = i
                image.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('products:detail', slug=product.slug)
    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(request, 'products/form.html', {
        'form': form,
        'formset': formset,
        'title': 'List New Product',
    })


@login_required
def product_edit(request, slug):
    product = get_object_or_404(Product, slug=slug, owner=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products:detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    return render(request, 'products/form.html', {
        'form': form,
        'formset': formset,
        'product': product,
        'title': 'Edit Product',
    })


@login_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug, owner=request.user)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
        return redirect('products:my_products')
    return render(request, 'products/confirm_delete.html', {'product': product})


@login_required
def toggle_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})


@login_required
def my_wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__owner').prefetch_related('product__images')
    return render(request, 'products/wishlist.html', {'items': items})


def check_availability(request, slug):
    product = get_object_or_404(Product, slug=slug)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        available = product.is_available_for_dates(start_date, end_date)
        return JsonResponse({'available': available})
    return JsonResponse({'error': 'Dates required'}, status=400)
