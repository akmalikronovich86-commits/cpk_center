from django.db import models
from django.utils import timezone

from apps.courses.models import AcademicGroup, Course
from apps.users.models import User


class Schedule(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Tasdiqlanmagan'),
        ('published', "E'lon qilingan"),
        ('cancelled', 'Bekor qilingan'),
    )

    group = models.ForeignKey(
        AcademicGroup,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name= 'Guruh'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name= 'Kurs'
    )
    lecturer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'lecturer'},
        related_name='lecturer_schedules',
        verbose_name= "O'qituvchi"
    )
    topic = models.ForeignKey(
        'courses.Topic',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedules',
        verbose_name= 'Mavzu'
    )
    date_start = models.DateTimeField(
        verbose_name= 'Boshlanish vaqti'
    )
    date_end = models.DateTimeField(
        verbose_name= 'Tugash vaqti'
    )
    room = models.CharField(
        max_length=50,
        blank=True,
        verbose_name= 'Auditoriya'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name= 'Holati'
    )
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='published_schedules',
        verbose_name= "Kim tomonidan e'lon qilingan"
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name= "E'lon qilingan sana"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_schedules',
        verbose_name= 'Kim tomonidan yaratilgan'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(
        blank=True,
        verbose_name= 'Izohlar'
    )
    duration_minutes = models.PositiveIntegerField(
        default=90,
        verbose_name= 'Dars davomiyligi (daqiqa)',
        help_text='Davomatni hisoblash uchun darsning to\'liq davomiyligi (daqiqalarda).'
    )

    class Meta:
        verbose_name =  'Dars '
        verbose_name_plural = 'Darslar'
        ordering = ['date_start']
        indexes = [
            models.Index(fields=['date_start', 'date_end']),
            models.Index(fields=['group', 'date_start']),
            models.Index(fields=['lecturer', 'date_start']),
        ]

    def get_duration(self):
        """Возвращает продолжительность в часах"""
        if self.date_start and self.date_end:
            delta = self.date_end - self.date_start
            hours = delta.total_seconds() / 3600
            return f"{hours:.1f}"
        return "0"

    def __str__(self):
        return f"{self.group.name} - {self.course.title} ({self.date_start.strftime('%d.%m.%Y %H:%M')})"

    @property
    def duration_hours(self):
        delta = self.date_end - self.date_start
        return delta.total_seconds() / 3600

    @property
    def effective_duration_minutes(self):
        """Darsning to'liq davomiyligi daqiqalarda.

        Agar boshlanish/tugash vaqtlari kiritilgan bo'lsa, ular asosida
        hisoblanadi, aks holda ``duration_minutes`` maydoni ishlatiladi.
        """
        if self.date_start and self.date_end:
            minutes = (self.date_end - self.date_start).total_seconds() / 60
            if minutes > 0:
                return int(round(minutes))
        return self.duration_minutes or 90

    def publish(self, user):
        self.status = 'published'
        self.published_by = user
        self.published_at = timezone.now()
        self.save()


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Qatnashgan'),
        ('absent', 'Qatnashmagan'),
        ('late', 'Kechikkan'),
        ('excused', 'Uzrli sabab'),
    )

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name= 'Dars'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='attendances',
        verbose_name= 'Tinglovchi'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='absent',
        verbose_name= 'Holati'
    )
    attended_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name= 'Qatnashgan daqiqalar',
        help_text='Tinglovchi darsda necha daqiqa qatnashgani. Kechikishlarni hisobga olish uchun ishlatiladi.'
    )
    notes = models.TextField(
        blank=True,
        verbose_name= 'Izohlar'
    )
    marked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendances',
        verbose_name= 'Kim tomonidan belgilangan'
    )
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name =  'Davomat '
        verbose_name_plural = 'Davomat'
        unique_together = ('schedule', 'student')

    def get_duration(self):
        """Возвращает продолжительность в часах"""
        if self.date_start and self.date_end:
            delta = self.date_end - self.date_start
            hours = delta.total_seconds() / 3600
            return f"{hours:.1f}"
        return "0"

    @property
    def counted_value(self):
        """Davomatning hisobga olinadigan qiymati (0, 0.5 yoki 1.0).

        Biznes-mantiq:
          * To'liq qatnashgan  -> 1.0
          * Darsning 50% dan ko'prog'ida qatnashgan (kechikkan) -> 0.5
          * Darsning 50% dan kamida qatnashgan -> 0.0
        """
        # Umuman kelmagan yoki uzrsiz sabab bilan yo'q
        if self.status == 'absent':
            return 0.0

        full_minutes = self.schedule.effective_duration_minutes if self.schedule_id else 90

        # Agar aniq daqiqalar kiritilgan bo'lsa — ular bo'yicha hisoblaymiz
        if self.attended_minutes is not None and full_minutes:
            ratio = self.attended_minutes / full_minutes
            if ratio >= 0.999:
                return 1.0
            if ratio > 0.5:
                return 0.5
            return 0.0

        # Aniq daqiqalar yo'q — status bo'yicha hisoblaymiz
        if self.status in ('present', 'excused'):
            return 1.0
        if self.status == 'late':
            return 0.5
        return 0.0

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.schedule} - {self.get_status_display()}"


# ==== CONFLICT-VALIDATION (audit 2026-08-17) ====
# Vaqt to'qnashuvlarini tekshirish: ma'ruzachi / guruh / xona
_original_schedule_clean = getattr(Schedule, 'clean', None)


def _schedule_clean_with_conflicts(self):
    from django.core.exceptions import ValidationError

    if _original_schedule_clean:
        _original_schedule_clean(self)

    date_start = getattr(self, 'date_start', None)
    date_end = getattr(self, 'date_end', None)
    if not (date_start and date_end):
        return

    qs = type(self).objects.all()
    if self.pk:
        qs = qs.exclude(pk=self.pk)

    errors = []
    for other in qs:
        o_start = getattr(other, 'date_start', None)
        o_end = getattr(other, 'date_end', None)
        if not (o_start and o_end):
            continue
        # Vaqt kesishishi: A_start < B_end AND B_start < A_end
        if not (date_start < o_end and o_start < date_end):
            continue

        # Ma'ruzachi band
        if getattr(self, 'lecturer_id', None) and self.lecturer_id == getattr(other, 'lecturer_id', None):
            lecturer_name = getattr(getattr(self.lecturer, 'user', None), 'full_name', "ma'ruzachi")
            errors.append(
                f"⚠️ Ma'ruzachi band ({lecturer_name}): "
                f"{o_start.strftime('%d.%m.%Y %H:%M')}-{o_end.strftime('%H:%M')} da dars bor"
            )
        # Guruh band
        if getattr(self, 'group_id', None) and self.group_id == getattr(other, 'group_id', None):
            errors.append(
                f"⚠️ Guruh band: {o_start.strftime('%d.%m.%Y %H:%M')}-{o_end.strftime('%H:%M')} da dars bor"
            )
        # Xona band
        room = getattr(self, 'room', None)
        o_room = getattr(other, 'room', None)
        if room and o_room and room == o_room:
            errors.append(
                f"⚠️ Xona band ({room}): {o_start.strftime('%d.%m.%Y %H:%M')}-{o_end.strftime('%H:%M')}"
            )

    if errors:
        raise ValidationError(errors)


Schedule.clean = _schedule_clean_with_conflicts
