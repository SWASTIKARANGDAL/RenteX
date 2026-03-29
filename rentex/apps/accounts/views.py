from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from .models import User
from .forms import ProfileUpdateForm
from apps.products.models import Product
from apps.bookings.models import Booking
from apps.payments.models import Payment


@login_required
def dashboard(request):
    user = request.user
    if user.is_owner:
        return owner_dashboard(request)
    return renter_dashboard(request)


@login_required
def renter_dashboard(request):
    user = request.user
    bookings = Booking.objects.filter(renter=user).select_related('product', 'product__owner').order_by('-created_at')
    active_bookings = bookings.filter(status__in=['confirmed', 'active'])
    pending_bookings = bookings.filter(status='pending')
    completed_bookings = bookings.filter(status='completed')
    total_spent = Payment.objects.filter(booking__renter=user, status='completed').aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'bookings': bookings[:5],
        'active_bookings': active_bookings,
        'pending_bookings': pending_bookings,
        'completed_bookings': completed_bookings,
        'total_spent': total_spent,
        'total_bookings': bookings.count(),
    }
    return render(request, 'dashboard/renter.html', context)


@login_required
def owner_dashboard(request):
    user = request.user
    products = Product.objects.filter(owner=user).annotate(
        booking_count=Count('bookings'),
        avg_rating_calc=Avg('reviews__rating')
    )
    bookings = Booking.objects.filter(product__owner=user).select_related('product', 'renter').order_by('-created_at')
    pending_bookings = bookings.filter(status='pending')
    total_earnings = Payment.objects.filter(
        booking__product__owner=user, status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_earnings = Payment.objects.filter(
        booking__product__owner=user,
        status='completed',
        created_at__month=__import__('datetime').date.today().month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'products': products,
        'bookings': bookings[:5],
        'pending_bookings': pending_bookings,
        'total_products': products.count(),
        'total_bookings': bookings.count(),
        'total_earnings': total_earnings,
        'monthly_earnings': monthly_earnings,
        'active_products': products.filter(is_available=True).count(),
    }
    return render(request, 'dashboard/owner.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


def public_profile(request, pk):
    profile_user = get_object_or_404(User, pk=pk)
    products = Product.objects.filter(owner=profile_user, is_available=True) if profile_user.is_owner else []
    from apps.reviews.models import Review
    reviews = Review.objects.filter(reviewed_user=profile_user).select_related('reviewer')
    context = {
        'profile_user': profile_user,
        'products': products,
        'reviews': reviews,
        'avg_rating': profile_user.get_avg_rating(),
    }
    return render(request, 'accounts/public_profile.html', context)
