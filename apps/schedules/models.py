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

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.schedule} - {self.get_status_display()}"
