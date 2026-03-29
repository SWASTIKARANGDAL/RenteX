from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_RENTER = 'renter'
    ROLE_OWNER = 'owner'
    ROLE_CHOICES = [
        (ROLE_RENTER, 'Renter'),
        (ROLE_OWNER, 'Owner'),
    ]

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_RENTER)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.email}"

    @property
    def is_owner(self):
        return self.role == self.ROLE_OWNER

    @property
    def is_renter(self):
        return self.role == self.ROLE_RENTER

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'

    def get_avg_rating(self):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(reviewed_user=self)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return None

    def get_total_earnings(self):
        if self.is_owner:
            from apps.payments.models import Payment
            return Payment.objects.filter(
                booking__product__owner=self,
                status='completed'
            ).aggregate(models.Sum('amount'))['amount__sum'] or 0
        return 0
