from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'full_name', 'phone', 'email', 'role', 'telegram_status', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'full_name', 'email', 'phone', 'telegram_user_id')
    ordering = ('username',)

    def telegram_status(self, obj):
        if obj.telegram_user_id:
            return format_html('<span style="color: green;">✅ {}</span>', obj.telegram_user_id)
        return format_html('<span style="color: gray;">❌ bog\'lanmagan</span>')
    telegram_status.short_description = 'Telegram'

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy malumotlar', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'full_name',
                'phone',
                'position',
            )
        }),
        ('Telegram', {
            'fields': ('telegram_user_id',),
            'description': 'Foydalanuvchi /start yuborganda bot ko\'rsatadigan ID ni shu yerga kiriting',
        }),
        ('Rol va holat', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
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
                'role',
            ),
        }),
    )
