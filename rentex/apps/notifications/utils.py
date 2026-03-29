from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .models import Notification


def create_notification(user, notification_type, title, message, link=''):
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )


def send_email_notification(to_email, subject, template, context):
    try:
        html_message = render_to_string(template, context)
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email error: {e}")


def send_booking_notification(booking, action):
    renter = booking.renter
    owner = booking.product.owner
    booking_url = reverse('bookings:detail', kwargs={'pk': booking.pk})

    messages_map = {
        'created': {
            'owner_title': f'New Booking Request: {booking.product.name}',
            'owner_msg': f'{renter.display_name} has requested to rent "{booking.product.name}" from {booking.start_date} to {booking.end_date}.',
            'renter_title': f'Booking #{booking.booking_number} Submitted',
            'renter_msg': f'Your booking request for "{booking.product.name}" has been submitted and is awaiting owner approval.',
        },
        'confirmed': {
            'renter_title': f'Booking #{booking.booking_number} Confirmed! 🎉',
            'renter_msg': f'Great news! Your booking for "{booking.product.name}" has been confirmed. Please complete your payment.',
        },
        'rejected': {
            'renter_title': f'Booking #{booking.booking_number} Rejected',
            'renter_msg': f'Unfortunately, your booking for "{booking.product.name}" was rejected. Note: {booking.owner_note}',
        },
        'cancelled': {
            'owner_title': f'Booking #{booking.booking_number} Cancelled',
            'owner_msg': f'The booking for "{booking.product.name}" by {renter.display_name} has been cancelled.',
            'renter_title': f'Booking #{booking.booking_number} Cancelled',
            'renter_msg': f'Your booking for "{booking.product.name}" has been cancelled.',
        },
        'completed': {
            'renter_title': f'Booking #{booking.booking_number} Completed',
            'renter_msg': f'Your rental of "{booking.product.name}" is complete. Please leave a review!',
        },
    }

    msg = messages_map.get(action, {})
    if not msg:
        return

    # Notify renter
    if 'renter_title' in msg:
        create_notification(renter, f'booking_{action}', msg['renter_title'], msg['renter_msg'], booking_url)
        send_email_notification(
            renter.email,
            msg['renter_title'],
            'emails/booking_notification.html',
            {'user': renter, 'booking': booking, 'action': action, 'message': msg['renter_msg']}
        )

    # Notify owner
    if 'owner_title' in msg:
        create_notification(owner, f'booking_{action}', msg['owner_title'], msg['owner_msg'], booking_url)
        send_email_notification(
            owner.email,
            msg['owner_title'],
            'emails/booking_notification.html',
            {'user': owner, 'booking': booking, 'action': action, 'message': msg['owner_msg']}
        )


def send_payment_notification(payment):
    booking = payment.booking
    renter = booking.renter
    owner = booking.product.owner

    create_notification(
        renter, 'payment_received',
        f'Payment Confirmed - ₹{payment.amount}',
        f'Your payment of ₹{payment.amount} for booking #{booking.booking_number} was successful.',
        reverse('payments:history')
    )
    create_notification(
        owner, 'payment_received',
        f'Payment Received - ₹{payment.amount}',
        f'Payment of ₹{payment.amount} received for "{booking.product.name}" from {renter.display_name}.',
        reverse('payments:history')
    )
