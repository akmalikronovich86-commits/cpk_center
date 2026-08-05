from django.contrib import admin
from .models import Certificate


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
