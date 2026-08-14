from django.db import models
from django.utils import timezone

from apps.users.models import User


class AssessmentRecord(models.Model):
    """Tinglovchining o'quv guruhi (dasturi) bo'yicha baholash yozuvi.

    Qatnashish va imtihon natijalarini jamlaydi, shuningdek Direktorning
    sertifikatni tasdiqlash va qayta topshirishga ruxsat berish qarorlarini saqlaydi.
    """

    # Biznes-logika chegaralari
    ATTENDANCE_THRESHOLD = 70  # % qatnashish
    EXAM_THRESHOLD = 70        # % to'g'ri javoblar

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='assessment_records',
        verbose_name='Tinglovchi',
    )
    group = models.ForeignKey(
        'courses.AcademicGroup',
        on_delete=models.CASCADE,
        related_name='assessment_records',
        verbose_name="O'quv guruhi",
    )

    # --- Qatnashish ---
    total_lessons = models.PositiveIntegerField(
        default=0,
        verbose_name="Jami mashg'ulotlar",
    )
    counted_attendances = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='Hisoblangan qatnashishlar',
    )
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Qatnashish, %',
    )
    attendance_passed = models.BooleanField(
        default=False,
        verbose_name='Qatnashish chegarasi o\'tilgan',
    )

    # --- Imtihon ---
    exam_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Imtihon natijasi, %',
    )
    exam_passed = models.BooleanField(
        default=False,
        verbose_name='Imtihon topshirilgan',
    )
    retake_allowed = models.BooleanField(
        default=False,
        verbose_name='Qayta topshirishga ruxsat',
    )
    retake_allowed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='allowed_retakes',
        verbose_name='Ruxsat bergan',
    )
    retake_allowed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Ruxsat berilgan sana',
    )
    retake_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Qayta topshirish natijasi, %',
    )
    retake_passed = models.BooleanField(
        default=False,
        verbose_name='Qayta topshirish topshirilgan',
    )

    # --- Yakuniy natija ---
    eligible_for_certificate = models.BooleanField(
        default=False,
        verbose_name='Sertifikatga ruxsat',
    )
    certificate_approved = models.BooleanField(
        default=False,
        verbose_name='Sertifikat tasdiqlangan',
    )
    certificate_approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_certificates_assessment',
        verbose_name='Tasdiqlagan',
    )
    certificate_approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Tasdiqlangan sana',
    )
    certificate = models.ForeignKey(
        'certificates.Certificate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assessment_records',
        verbose_name='Berilgan sertifikat',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan')

    class Meta:
        verbose_name = 'Attestatsiya yozuvi'
        verbose_name_plural = 'Attestatsiya yozuvlari'
        unique_together = ('student', 'group')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} — {self.group.name}"

    @property
    def final_exam_passed(self):
        """Imtihon topshirilgan deb hisoblanadi, agar asosiy yoki qayta topshirish topshirilgan bo'lsa."""
        return bool(self.exam_passed or self.retake_passed)

    @property
    def status_label(self):
        """Yozuv holati (interfeys uchun)."""
        if self.certificate_approved:
            return 'Sertifikat tasdiqlangan'
        if self.eligible_for_certificate:
            return 'Sertifikatga tayyor'
        if not self.exam_passed and self.retake_allowed and not self.retake_passed:
            return 'Qayta topshirish tayinlangan'
        if not self.exam_passed and not self.retake_passed:
            return 'Imtihon topshirilmagan'
        if not self.attendance_passed:
            return 'Qatnashish yetarli emas'
        return 'Jarayonda'
