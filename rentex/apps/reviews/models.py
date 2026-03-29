from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    REVIEW_TYPE_PRODUCT = 'product'
    REVIEW_TYPE_USER = 'user'
    TYPE_CHOICES = [(REVIEW_TYPE_PRODUCT, 'Product'), (REVIEW_TYPE_USER, 'User')]

    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews_received')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, null=True, blank=True, related_name='review')
    review_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=REVIEW_TYPE_PRODUCT)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.reviewer} - {self.rating}★"

    @property
    def stars_range(self):
        return range(1, 6)
