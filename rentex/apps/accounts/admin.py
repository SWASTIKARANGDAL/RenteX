from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'get_full_name', 'role', 'is_verified', 'date_joined']
    list_filter = ['role', 'is_verified', 'is_active', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone']
    fieldsets = UserAdmin.fieldsets + (
        ('RenteX Info', {'fields': ('role', 'phone', 'avatar', 'bio', 'city', 'state', 'pincode', 'is_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('RenteX Info', {'fields': ('email', 'role', 'phone')}),
    )
    ordering = ['-date_joined']
