from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Review
from apps.bookings.models import Booking
from apps.products.models import Product


@login_required
def create_review(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, renter=request.user, status='completed')

    if hasattr(booking, 'review'):
        messages.info(request, "You have already reviewed this booking.")
        return redirect('bookings:detail', pk=booking_pk)

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')

        Review.objects.create(
            reviewer=request.user,
            reviewed_user=booking.product.owner,
            product=booking.product,
            booking=booking,
            review_type='product',
            rating=rating,
            title=title,
            comment=comment,
        )
        messages.success(request, "Review submitted successfully!")
        return redirect('bookings:detail', pk=booking_pk)

    return render(request, 'reviews/create.html', {'booking': booking})


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, reviewer=request.user)
    if request.method == 'POST':
        review.delete()
        messages.success(request, "Review deleted.")
        return redirect('accounts:dashboard')
    return render(request, 'reviews/confirm_delete.html', {'review': review})


def product_reviews(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = Review.objects.filter(product=product, is_approved=True).select_related('reviewer')
    return render(request, 'reviews/product_reviews.html', {'product': product, 'reviews': reviews})
