from django.contrib import admin
from .models import AttendanceToken


@admin.register(AttendanceToken)
class AttendanceTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'schedule', 'is_used', 'used_by', 'used_at', 'expires_at')
    list_filter = ('is_used',)
    readonly_fields = ('token', 'secret', 'created_at', 'used_at', 'used_by')
