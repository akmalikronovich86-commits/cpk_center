from django.contrib import admin

from .models import Announcement, Certificate


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'created_by')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)

    fieldsets = (
        ('E\'lon ma\'lumotlari', {
            'fields': ('title', 'content', 'is_active')
        }),
        ('Tizim ma\'lumotlari', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        'certificate_number',
        'student',
        'course',
        'issue_date',
        'status',
        'created_at'
    )
    list_filter = ('status', 'issue_date', 'course')
    search_fields = ('certificate_number', 'qr_code', 'student__full_name')
    ordering = ('-issue_date',)
    readonly_fields = ('certificate_number', 'qr_code', 'created_at', 'updated_at')

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': (
                'student',
                'course',
                'series',
                'certificate_number',
                'issue_date',
                'expiry_date'
            )
        }),
        ('Holat va tekshirish', {
            'fields': (
                'status',
                'qr_code',
                'pdf_file',
                'registry_number'
            )
        }),
        ('Tizim ma\'lumotlari', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            )
        }),
    )
