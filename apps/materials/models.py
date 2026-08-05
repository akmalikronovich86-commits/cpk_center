from django.db import models
from django.utils import timezone
from apps.courses.models import Course
from apps.users.models import User
import os

def material_upload_path(instance, filename):
    return f"materials/course_{instance.course.id}/{instance.type}/{filename}"

class Material(models.Model):
    TYPE_CHOICES = (
        ('document', 'Hujjat'),
        ('presentation', 'Taqdimot'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('animation', 'Animatsiya'),
        ('test', 'Test'),
        ('program', "O'quv dasturi"),
        ('control_questions', 'Nazorat savollari'),
        ('additional', "Qo'shimcha material"),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name= 'Kurs'
    )
    title = models.CharField(
        max_length=255,
        verbose_name= 'Nomi'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name= 'Turi'
    )
    file = models.FileField(
        upload_to=material_upload_path,
        verbose_name= 'Fayl'
    )
    description = models.TextField(
        blank=True,
        verbose_name= 'Tavsif'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'lecturer'},
        related_name='uploaded_materials',
        verbose_name= 'Kim tomonidan yuklangan'
    )
    uploaded_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(
        default=False,
        verbose_name= "E'lon qilingan"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name= 'Tartib raqami'
    )
    file_size = models.PositiveIntegerField(
        default=0,
        verbose_name= 'Fayl hajmi (bayt)'
    )

    class Meta:
        verbose_name =  'Material '
        verbose_name_plural = 'Materiallar'
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"{self.course.code} - {self.title} ({self.get_type_display()})"

    def save(self, *args, **kwargs):
        if self.file:
            try:
                self.file_size = self.file.size
            except (FileNotFoundError, OSError):
                self.file_size = 0
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)
