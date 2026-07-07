from django.db import models
from django.utils import timezone


class Certificate(models.Model):
    """Сертификат о повышении квалификации"""
    
    STATUS_CHOICES = [
        ('issued', 'Berilgan'),
        ('revoked', "Bekor qilingan"),
        ('duplicate', 'Dublikat'),
        ('draft', 'Loyiha'),
    ]
    
    # Связи
    student = models.ForeignKey(
        'groups.StudentRecord',
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name="Tinglovchi"
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name="Kurs"
    )
    
    # Данные сертификата
    series = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Seriya"
    )
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Sertifikat raqami"
    )
    issue_date = models.DateField(
        default=timezone.now,
        verbose_name="Berilgan sana"
    )
    expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Amal qilish muddati"
    )
    
    # QR-код для проверки
    qr_code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="QR kod"
    )
    qr_image = models.ImageField(
        upload_to='certificates/qr/',
        blank=True,
        null=True,
        verbose_name="QR rasm"
    )
    
    # PDF файл
    pdf_file = models.FileField(
        upload_to='certificates/pdf/',
        blank=True,
        null=True,
        verbose_name="PDF fayl"
    )
    
    # Статус
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Holat"
    )
    
    # Реестр МЙҲТ
    registry_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ro'yxat raqami (MYHT)"
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_certificates',
        verbose_name="Yaratgan"
    )
    
    class Meta:
        verbose_name = "Sertifikat"
        verbose_name_plural = "Sertifikatlar"
        ordering = ['-issue_date', '-certificate_number']
        indexes = [
            models.Index(fields=['certificate_number'], name='idx_cert_number'),
            models.Index(fields=['qr_code'], name='idx_cert_qr'),
            models.Index(fields=['student', 'course'], name='idx_cert_student_course'),
        ]
    
    def __str__(self):
        return f"Sertifikat {self.certificate_number} - {self.student.full_name}"
