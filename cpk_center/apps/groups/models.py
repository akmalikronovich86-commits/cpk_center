from django.core.exceptions import ValidationError
from django.db import models


class ActiveStudentManager(models.Manager):
    """Кастомный менеджер для активных студентов текущего учебного года"""
    def get_queryset(self):
        return super().filter(
            training_year__name='2025-2026',
            user__is_active=True
        )


class TrainingYear(models.Model):
    """O'quv yillari"""
    name = models.CharField(max_length=10, unique=True, verbose_name="Yil nomi")

    class Meta:
        verbose_name = "O'quv yili"
        verbose_name_plural = "O'quv yillari"
        ordering = ['-name']

    def __str__(self):
        return self.name


class StudentRecord(models.Model):
    """Tinglovchi ma'lumotlari"""
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='student_record',
        verbose_name="Foydalanuvchi"
    )
    xtm = models.CharField(max_length=100, blank=True, null=True, verbose_name="XTM kodi")
    full_name = models.CharField(max_length=300, blank=True, null=True, verbose_name="Malaka oshiruvchi (FIO)")
    position = models.CharField(max_length=300, blank=True, null=True, verbose_name="Lavozimi")
    passport = models.CharField(max_length=50, blank=True, null=True, verbose_name="Pasport")
    birth_date = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tug'ilgan sanasi")
    group = models.CharField(max_length=50, blank=True, null=True, verbose_name="Guruhi")
    branch = models.CharField(max_length=200, blank=True, null=True, verbose_name="Hududiy filial nomi")
    district_power = models.CharField(max_length=200, blank=True, null=True, verbose_name="Tuman elektr ta'minoti")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telefon raqami")
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email")
    grade = models.CharField(max_length=50, blank=True, null=True, verbose_name="Yakuniy bahosi")
    topic = models.TextField(blank=True, null=True, verbose_name="Mustaqil ta'lim mavzusi")
    period = models.CharField(max_length=100, blank=True, null=True, verbose_name="Malaka oshirish muddati")

    training_year = models.ForeignKey(
        TrainingYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="O'quv yili"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    # Кастомные менеджеры
    objects = models.Manager()  # Стандартный менеджер
    active_students = ActiveStudentManager()  # Кастомный менеджер

    class Meta:
        verbose_name = "Tinglovchi"
        verbose_name_plural = "Ma'lumotlar bazasi"
        ordering = ['full_name']
        # Индексы для оптимизации частых запросов
        indexes = [
            models.Index(fields=['passport'], name='idx_studentrecord_passport'),
            models.Index(fields=['phone'], name='idx_studentrecord_phone'),
            models.Index(fields=['training_year', 'branch'], name='idx_studentrecord_year_branch'),
        ]

    def clean(self):
        """Валидация данных"""
        super().clean()
        if self.phone:
            clean_phone = self.phone.replace(' ', '').replace('-', '').replace('.', '')
            if not clean_phone.startswith('+998') and len(clean_phone) != 12:
                # Мягкая валидация - только предупреждение для старых данных
                pass  # Не блокируем старые данные

    def clean_phone(self):
        """Валидация телефона для форм"""
        if self.phone:
            phone = self.phone.replace(' ', '').replace('-', '').replace('.', '')
            if not phone.startswith('+998') or len(phone) != 12:
                raise ValidationError("Noto'g'ri telefon raqami")
            return phone
        return self.phone

    def __str__(self):
        return f"{self.full_name} ({self.passport})"
