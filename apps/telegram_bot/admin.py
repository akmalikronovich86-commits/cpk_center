from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

User = get_user_model()


@admin.register(User)
class UserTelegramAdmin(admin.ModelAdmin):
    """Admin interfeys - Telegram bilan bog'langan foydalanuvchilar"""
    list_display = ('username', 'full_name', 'role', 'telegram_status', 'telegram_user_id')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'full_name', 'email', 'telegram_user_id')
    readonly_fields = ('telegram_user_id',)
    
    def telegram_status(self, obj):
        if obj.telegram_user_id:
            return format_html(
                '<span style="color: green;">✅ Bog\'langan</span>'
            )
        return format_html(
            '<span style="color: gray;">❌ Bog\'lanmagan</span>'
        )
    telegram_status.short_description = 'Telegram holati'
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'email', 'full_name', 'phone')
        }),
        ('Telegram', {
            'fields': ('telegram_user_id',),
            'description': 'Telegram ID avtomatik to\'ldiriladi'
        }),
        ('Rol va holat', {
            'fields': ('role', 'is_active', 'is_staff')
        }),
    )
