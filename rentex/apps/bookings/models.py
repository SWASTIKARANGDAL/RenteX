from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_number = models.CharField(max_length=20, unique=True, blank=True)
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings_as_renter')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.PositiveIntegerField(default=1)
    rental_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    renter_note = models.TextField(blank=True)
    owner_note = models.TextField(blank=True)
    pickup_address = models.TextField(blank=True)
    return_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.booking_number:
            import random, string
            self.booking_number = 'BK' + ''.join(random.choices(string.digits, k=8))
        if not self.total_days:
            delta = self.end_date - self.start_date
            self.total_days = max(delta.days, 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.booking_number} - {self.product.name}"

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days or 1

    @property
    def can_review(self):
        return self.status == self.STATUS_COMPLETED

    @property
    def is_active_or_upcoming(self):
        return self.status in [self.STATUS_CONFIRMED, self.STATUS_ACTIVE]

    def confirm(self):
        self.status = self.STATUS_CONFIRMED
        self.confirmed_at = timezone.now()
        self.save()

    def reject(self, note=''):
        self.status = self.STATUS_REJECTED
        self.owner_note = note
        self.save()

    def cancel(self):
        self.status = self.STATUS_CANCELLED
        self.save()

    def complete(self):
        self.status = self.STATUS_COMPLETED
        self.completed_at = timezone.now()
        self.save()

    def get_status_badge_class(self):
        badges = {
            'pending': 'warning',
            'confirmed': 'info',
            'active': 'primary',
            'completed': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
        }
        return badges.get(self.status, 'secondary')
