from django.db import models
from django.utils import timezone

from apps.users.models import User


class AssessmentRecord(models.Model):
    """Сводная запись оценки слушателя по учебной группе (программе).

    Агрегирует посещаемость и результаты экзамена, а также хранит
    решения Директора об утверждении сертификата и допуске к пересдаче.
    """

    # Пороговые значения бизнес-логики
    ATTENDANCE_THRESHOLD = 70  # % посещаемости
    EXAM_THRESHOLD = 70        # % правильных ответов

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='assessment_records',
        verbose_name='Слушатель',
    )
    group = models.ForeignKey(
        'courses.AcademicGroup',
        on_delete=models.CASCADE,
        related_name='assessment_records',
        verbose_name='Учебная группа',
    )

    # --- Посещаемость ---
    total_lessons = models.PositiveIntegerField(
        default=0,
        verbose_name='Всего занятий',
    )
    counted_attendances = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='Зачтённые посещения',
    )
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Посещаемость, %',
    )
    attendance_passed = models.BooleanField(
        default=False,
        verbose_name='Порог посещаемости пройден',
    )

    # --- Экзамен ---
    exam_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Результат экзамена, %',
    )
    exam_passed = models.BooleanField(
        default=False,
        verbose_name='Экзамен сдан',
    )
    retake_allowed = models.BooleanField(
        default=False,
        verbose_name='Пересдача разрешена',
    )
    retake_allowed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='allowed_retakes',
        verbose_name='Пересдачу разрешил',
    )
    retake_allowed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата разрешения пересдачи',
    )
    retake_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Результат пересдачи, %',
    )
    retake_passed = models.BooleanField(
        default=False,
        verbose_name='Пересдача сдана',
    )

    # --- Итог ---
    eligible_for_certificate = models.BooleanField(
        default=False,
        verbose_name='Допущен к сертификату',
    )
    certificate_approved = models.BooleanField(
        default=False,
        verbose_name='Сертификат утверждён',
    )
    certificate_approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_certificates_assessment',
        verbose_name='Сертификат утвердил',
    )
    certificate_approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата утверждения сертификата',
    )
    certificate = models.ForeignKey(
        'certificates.Certificate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assessment_records',
        verbose_name='Выданный сертификат',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Запись аттестации'
        verbose_name_plural = 'Записи аттестации'
        unique_together = ('student', 'group')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} — {self.group.name}"

    @property
    def final_exam_passed(self):
        """Экзамен считается сданным, если сдан основной либо пересдача."""
        return bool(self.exam_passed or self.retake_passed)

    @property
    def status_label(self):
        """Человекочитаемый статус записи (для интерфейса)."""
        if self.certificate_approved:
            return 'Сертификат утверждён'
        if self.eligible_for_certificate:
            return 'Готов к сертификату'
        if not self.exam_passed and self.retake_allowed and not self.retake_passed:
            return 'Назначена пересдача'
        if not self.exam_passed and not self.retake_passed:
            return 'Экзамен не сдан'
        if not self.attendance_passed:
            return 'Недостаточная посещаемость'
        return 'В процессе'
