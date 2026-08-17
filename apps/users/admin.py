from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'full_name', 'phone', 'email', 'role', 'telegram_user_id', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'full_name', 'email', 'phone', 'telegram_user_id')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy malumotlar', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'full_name',
                'phone',
                'telegram_user_id',
                'position'
            )
        }),
        ('Rol va holat', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Muhim malumotlar', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'full_name',
                'phone',
                'email',
                'role'
            ),
        }),
    )
