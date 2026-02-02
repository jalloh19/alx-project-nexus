"""User admin configuration."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_verified', 'is_staff']
    list_filter = ['is_verified', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_verified',)}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""
    list_display = ['user', 'preferred_language', 'mature_content', 'created_at']
    list_filter = ['preferred_language', 'mature_content', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
