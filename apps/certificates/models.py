from django.db import models
from django.utils import timezone
import secrets


class Announcement(models.Model):
    """E'lonlar - tinglovchilar uchun xabarlar"""
    
    title = models.CharField(
        max_length=255,
        verbose_name="Sarlavha"
    )
    content = models.TextField(
        verbose_name="Matn"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Yaratgan"
    )
    
    class Meta:
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Certificate(models.Model):
    """Sertifikat - malaka oshirish haqida guvohnoma"""

    STATUS_CHOICES = [
        ('issued', 'Berilgan'),
        ('revoked', 'Bekor qilingan'),
        ('duplicate', 'Dublikat'),
        ('draft', 'Loyiha'),
    ]

    # Aloqalar
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

    # Sertifikat ma'lumotlari
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

    # QR-kod
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

    # PDF fayl
    pdf_file = models.FileField(
        upload_to='certificates/pdf/',
        blank=True,
        null=True,
        verbose_name="PDF fayl"
    )

    # Holat
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Holat"
    )

    # MYHT reyestri
    registry_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ro'yxat raqami (MYHT)"
    )

    # Tizim ma'lumotlari
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
        name = self.student.full_name if self.student else "Noma'lum"
        return f"Sertifikat {self.certificate_number} - {name}"

    def save(self, *args, **kwargs):
        # Avtomatik raqam generatsiya
        if not self.certificate_number:
            self.certificate_number = self._generate_number()

        # Avtomatik QR-kod generatsiya
        if not self.qr_code:
            self.qr_code = self._generate_qr_code()

        # Avtomatik amal qilish muddati (5 yil)
        if not self.expiry_date and self.issue_date:
            try:
                self.expiry_date = self.issue_date.replace(year=self.issue_date.year + 5)
            except ValueError:
                # 29 fevral uchun
                self.expiry_date = self.issue_date.replace(year=self.issue_date.year + 5, day=28)

        super().save(*args, **kwargs)

    def _generate_number(self):
        """Sertifikat raqamini avtomatik generatsiya qilish"""
        year = timezone.now().year
        prefix = f'CERT-{year}-'
        last_cert = Certificate.objects.filter(
            certificate_number__startswith=prefix
        ).order_by('-certificate_number').first()

        if last_cert and last_cert.certificate_number:
            try:
                last_num = int(last_cert.certificate_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1

        return f'{prefix}{new_num:05d}'

    def _generate_qr_code(self):
        """Unikal QR-kod generatsiya qilish"""
        random_hash = secrets.token_hex(4)
        number = self.certificate_number or 'DRAFT'
        return f'CPK-{number}-{random_hash}'

    def revoke(self):
        """Sertifikatni bekor qilish"""
        self.status = 'revoked'
        self.save(update_fields=['status', 'updated_at'])

    def create_duplicate(self):
        """Dublikat yaratish"""
        return Certificate.objects.create(
            student=self.student,
            course=self.course,
            series=self.series,
            issue_date=self.issue_date,
            expiry_date=self.expiry_date,
            status='duplicate',
            registry_number=self.registry_number,
            created_by=self.created_by,
        )
