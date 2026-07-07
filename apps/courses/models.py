from django.db import models
from django.utils import timezone
from apps.users.models import User

class Course(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name= 'Nomi'
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name= 'Kurs kodi'
    )
    description = models.TextField(
        blank=True,
        verbose_name= 'Tavsif'
    )
    duration_hours = models.PositiveIntegerField(
        verbose_name= 'Davomiyligi (soat)'
    )
    lecturer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'lecturer'},
        related_name='courses',
        verbose_name= "O'qituvchi"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True,
        verbose_name= 'Faol'
    )
    class Meta:
        verbose_name =  "Mavjud kurs "
        verbose_name_plural = "Mavjud kurslar"


    def __str__(self):
        return f"{self.code} - {self.title}"


class AcademicGroup(models.Model):
    class Meta:
        db_table = 'courses_group'  # Сохраняем старое имя таблицы
        verbose_name =  "O'quv guruhi "
        verbose_name_plural = "O'quv guruhlari"
    name = models.CharField(
        max_length=100,
        verbose_name= 'Guruh nomi'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='academic_groups',
        verbose_name= 'Kurs'
    )
    students = models.ManyToManyField(
        User,
        through='Enrollment',
        related_name='course_groups',
        limit_choices_to={'role': 'student'},
        verbose_name= 'Tinglovchilar'
    )
    start_date = models.DateField(
        verbose_name= 'Boshlanish sanasi'
    )
    end_date = models.DateField(
        verbose_name= 'Tugash sanasi'
    )
    max_students = models.PositiveIntegerField(
        default=30,
        verbose_name= 'Maks. tinglovchilar'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name} ({self.course.code})"
class Enrollment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        verbose_name= 'Tinglovchi'
    )
    group = models.ForeignKey(
        AcademicGroup,
        on_delete=models.CASCADE,
        verbose_name= 'Guruh'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        verbose_name= 'Faol'
    )
    class Meta:
        verbose_name =  "Kursga yozilish "
        verbose_name_plural = "Kursga yozilish"


    def __str__(self):
        return f"{self.student.get_full_name()} -> {self.group.name}"


class Topic(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='topics',
        verbose_name= 'Kurs'
    )
    title = models.CharField(
        max_length=255,
        verbose_name= 'Mavzu nomi'
    )
    description = models.TextField(
        blank=True,
        verbose_name= 'Tavsif'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name= 'Tartib raqami'
    )
    duration_hours = models.PositiveIntegerField(
        default=1,
        verbose_name= 'Davomiyligi (soat)'
    )
    class Meta:
        verbose_name =  "Kursga oid mavzu "
        verbose_name_plural = "Kursga oid mavzular"


    def __str__(self):
        return f"{self.course.code} - {self.title}"
