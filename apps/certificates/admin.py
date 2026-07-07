from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from import_export.admin import ExportMixin
from import_export import resources
from .models import Certificate


# Сначала определяем Ресурс для экспорта
class CertificateResource(resources.ModelResource):
    class Meta:
        model = Certificate
        fields = (
            'certificate_number',
            'student__full_name',
            'course__title',
            'course__code',
            'issue_date',
            'expiry_date',
            'status',
            'qr_code',
            'created_at'
        )
        verbose_name = 'Sertifikatlar'


# Теперь класс Админки
@admin.register(Certificate)
class CertificateAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = CertificateResource

    list_display = (
        'certificate_number',
        'student',
        'course',
        'issue_date',
        'status',
        'pdf_button',
        'verify_button',
        'created_at'
    )
    list_filter = ('status', 'issue_date', 'course')
    search_fields = ('certificate_number', 'qr_code', 'student__full_name')
    ordering = ('-issue_date',)
    readonly_fields = ('certificate_number', 'qr_code', 'created_at', 'updated_at', 'pdf_button', 'verify_button')

    fieldsets = (
        ('Asosiy malumotlar', {
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
                'pdf_button',
                'verify_button',
                'registry_number'
            )
        }),
        ('Tizim malumotlari', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            )
        }),
    )

    def pdf_button(self, obj):
        if obj.pk:
            url = reverse('certificates:generate_pdf', args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" style="padding: 6px 12px; background: #1e3a5f; color: white; text-decoration: none; border-radius: 4px; display: inline-block;">PDF yuklash</a>',
                url
            )
        return '-'
    pdf_button.short_description = 'PDF'

    def verify_button(self, obj):
        if obj.pk and obj.qr_code:
            url = reverse('certificates:verify', args=[obj.qr_code])
            return format_html(
                '<a href="{}" target="_blank" style="padding: 6px 12px; background: #48bb78; color: white; text-decoration: none; border-radius: 4px; display: inline-block;">Tekshirish</a>',
                url
            )
        return '-'
    verify_button.short_description = 'Tekshirish'

    actions = ['revoke_certificates', 'create_duplicates']

    def revoke_certificates(self, request, queryset):
        count = 0
        for cert in queryset:
            cert.revoke()
            count += 1
        self.message_user(request, f"{count} ta sertifikat bekor qilindi")
    revoke_certificates.short_description = "Sertifikatlarni bekor qilish"

    def create_duplicates(self, request, queryset):
        count = 0
        for cert in queryset:
            cert.create_duplicate()
            count += 1
        self.message_user(request, f"{count} ta dublikat yaratildi")
    create_duplicates.short_description = "Dublikat yaratish"
