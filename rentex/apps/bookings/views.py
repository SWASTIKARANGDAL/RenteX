from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import date, timedelta
from decimal import Decimal
from .models import Booking
from apps.products.models import Product
from apps.notifications.utils import send_booking_notification


@login_required
def create_booking(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)

    if request.user == product.owner:
        messages.error(request, "You cannot book your own product.")
        return redirect('products:detail', slug=slug)

    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        renter_note = request.POST.get('renter_note', '')

        try:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid dates provided.")
            return redirect('products:detail', slug=slug)

        if start_date < date.today():
            messages.error(request, "Start date cannot be in the past.")
            return redirect('products:detail', slug=slug)

        if end_date <= start_date:
            messages.error(request, "End date must be after start date.")
            return redirect('products:detail', slug=slug)

        if not product.is_available_for_dates(start_date, end_date):
            messages.error(request, "Product is not available for the selected dates.")
            return redirect('products:detail', slug=slug)

        total_days = (end_date - start_date).days
        rental_amount = product.get_price_for_days(total_days)
        deposit_amount = product.deposit_amount
        total_amount = Decimal(str(rental_amount)) + deposit_amount

        booking = Booking.objects.create(
            renter=request.user,
            product=product,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            rental_amount=rental_amount,
            deposit_amount=deposit_amount,
            total_amount=total_amount,
            renter_note=renter_note,
        )

        send_booking_notification(booking, 'created')
        messages.success(request, f"Booking #{booking.booking_number} created! Waiting for owner confirmation.")
        return redirect('bookings:detail', pk=booking.pk)

    # GET - show booking form
    start_date = request.GET.get('start_date', str(date.today() + timedelta(days=1)))
    end_date = request.GET.get('end_date', str(date.today() + timedelta(days=3)))
    try:
        from datetime import datetime
        sd = datetime.strptime(start_date, '%Y-%m-%d').date()
        ed = datetime.strptime(end_date, '%Y-%m-%d').date()
        total_days = max((ed - sd).days, 1)
        estimated_amount = product.get_price_for_days(total_days)
    except Exception:
        total_days = 2
        estimated_amount = product.price_per_day * 2

    return render(request, 'bookings/create.html', {
        'product': product,
        'start_date': start_date,
        'end_date': end_date,
        'total_days': total_days,
        'estimated_amount': estimated_amount,
        'today': date.today(),
    })


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user not in [booking.renter, booking.product.owner]:
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard')
    return render(request, 'bookings/detail.html', {'booking': booking})


@login_required
def booking_list(request):
    user = request.user
    if user.is_owner:
        bookings = Booking.objects.filter(product__owner=user).select_related('product', 'renter')
    else:
        bookings = Booking.objects.filter(renter=user).select_related('product', 'product__owner')

    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    return render(request, 'bookings/list.html', {
        'bookings': bookings,
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES,
    })


@login_required
def confirm_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, product__owner=request.user, status='pending')
    if request.method == 'POST':
        booking.confirm()
        send_booking_notification(booking, 'confirmed')
        messages.success(request, f"Booking #{booking.booking_number} confirmed!")
    return redirect('bookings:detail', pk=pk)


@login_required
def reject_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, product__owner=request.user, status='pending')
    if request.method == 'POST':
        note = request.POST.get('note', '')
        booking.reject(note)
        send_booking_notification(booking, 'rejected')
        messages.success(request, f"Booking #{booking.booking_number} rejected.")
    return redirect('bookings:detail', pk=pk)


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user not in [booking.renter, booking.product.owner]:
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard')
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, "This booking cannot be cancelled.")
        return redirect('bookings:detail', pk=pk)
    if request.method == 'POST':
        booking.cancel()
        send_booking_notification(booking, 'cancelled')
        messages.success(request, f"Booking #{booking.booking_number} cancelled.")
    return redirect('bookings:detail', pk=pk)


@login_required
def complete_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, product__owner=request.user, status='confirmed')
    if request.method == 'POST':
        booking.complete()
        send_booking_notification(booking, 'completed')
        messages.success(request, f"Booking #{booking.booking_number} marked as completed!")
    return redirect('bookings:detail', pk=pk)


@login_required
def generate_invoice(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user not in [booking.renter, booking.product.owner]:
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard')
    return render(request, 'bookings/invoice.html', {'booking': booking})


@login_required
def calculate_price(request):
    product_id = request.GET.get('product_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    try:
        product = Product.objects.get(id=product_id)
        from datetime import datetime
        sd = datetime.strptime(start_date, '%Y-%m-%d').date()
        ed = datetime.strptime(end_date, '%Y-%m-%d').date()
        days = max((ed - sd).days, 1)
        amount = product.get_price_for_days(days)
        total = float(amount) + float(product.deposit_amount)
        return JsonResponse({
            'days': days,
            'rental_amount': float(amount),
            'deposit_amount': float(product.deposit_amount),
            'total_amount': total,
            'available': product.is_available_for_dates(sd, ed),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
