from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from .models import Payment
from apps.bookings.models import Booking
import json


def get_razorpay_client():
    try:
        import razorpay
        return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    except ImportError:
        return None


@login_required
def payment_initiate(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, renter=request.user)

    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, "This booking is not eligible for payment.")
        return redirect('bookings:detail', pk=booking_pk)

    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={'amount': booking.total_amount, 'gateway': settings.PAYMENT_GATEWAY}
    )

    if settings.PAYMENT_GATEWAY == 'razorpay':
        client = get_razorpay_client()
        if client:
            try:
                order_data = {
                    'amount': payment.amount_in_paise,
                    'currency': 'INR',
                    'receipt': str(booking.booking_number),
                    'notes': {
                        'booking_id': str(booking.id),
                        'renter': booking.renter.email,
                    }
                }
                order = client.order.create(data=order_data)
                payment.gateway_order_id = order['id']
                payment.save()
            except Exception as e:
                # Demo mode - use fake order ID
                payment.gateway_order_id = f'order_demo_{booking.booking_number}'
                payment.save()
        else:
            payment.gateway_order_id = f'order_demo_{booking.booking_number}'
            payment.save()

    context = {
        'booking': booking,
        'payment': payment,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'stripe_key': settings.STRIPE_PUBLISHABLE_KEY,
        'gateway': settings.PAYMENT_GATEWAY,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_success(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, renter=request.user)
    payment = get_object_or_404(Payment, booking=booking)

    if request.method == 'POST':
        gateway_payment_id = request.POST.get('razorpay_payment_id', request.POST.get('stripe_payment_id', ''))
        gateway_signature = request.POST.get('razorpay_signature', '')

        # Verify payment (simplified - in prod use proper verification)
        payment.gateway_payment_id = gateway_payment_id
        payment.gateway_signature = gateway_signature
        payment.status = 'completed'
        payment.paid_at = timezone.now()
        payment.save()

        # Confirm booking
        if booking.status == 'pending':
            booking.confirm()

        from apps.notifications.utils import send_payment_notification
        send_payment_notification(payment)

        messages.success(request, f"Payment successful! Booking #{booking.booking_number} is confirmed.")
        return redirect('bookings:detail', pk=booking_pk)

    return render(request, 'payments/success.html', {'booking': booking, 'payment': payment})


@csrf_exempt
def razorpay_webhook(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            event = payload.get('event')

            if event == 'payment.captured':
                payment_entity = payload['payload']['payment']['entity']
                order_id = payment_entity.get('order_id')
                try:
                    payment = Payment.objects.get(gateway_order_id=order_id)
                    payment.status = 'completed'
                    payment.gateway_payment_id = payment_entity['id']
                    payment.paid_at = timezone.now()
                    payment.save()
                    payment.booking.confirm()
                except Payment.DoesNotExist:
                    pass
        except Exception:
            pass
    return HttpResponse(status=200)


@login_required
def payment_history(request):
    user = request.user
    if user.is_owner:
        payments = Payment.objects.filter(booking__product__owner=user).select_related('booking', 'booking__renter', 'booking__product')
    else:
        payments = Payment.objects.filter(booking__renter=user).select_related('booking', 'booking__product')
    return render(request, 'payments/history.html', {'payments': payments})


@login_required
def demo_payment_complete(request, booking_pk):
    """Demo endpoint to simulate payment completion for testing"""
    booking = get_object_or_404(Booking, pk=booking_pk, renter=request.user)
    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={'amount': booking.total_amount, 'gateway': 'razorpay'}
    )
    payment.status = 'completed'
    payment.gateway_payment_id = f'pay_demo_{booking.booking_number}'
    payment.paid_at = timezone.now()
    payment.save()
    if booking.status == 'pending':
        booking.confirm()
    messages.success(request, f"[DEMO] Payment of ₹{payment.amount} completed! Booking confirmed.")
    return redirect('bookings:detail', pk=booking_pk)
