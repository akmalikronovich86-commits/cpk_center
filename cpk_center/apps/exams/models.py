from django.db import models

from apps.courses.models import Course
from apps.users.models import User


class ExamQuestion(models.Model):
    TYPE_CHOICES = (
        ('single', "Bitta to'g'ri javob"),
        ('multiple', 'Bir nechta to\'g\'ri javob'),
        ('open', 'Ochiq javob'),
        ('true_false', "To'g'ri/Noto'g'ri"),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name= 'Kurs'
    )
    question_text = models.TextField(
        verbose_name= 'Savol matni'
    )
    type = models.CharField(
        max_length=15,
        choices=TYPE_CHOICES,
        verbose_name= 'Savol turi'
    )
    options = models.JSONField(
        default=list,
        verbose_name= 'Javob variantlari',
        help_text="Single/multiple uchun variantlar massivi. Open uchun bo'sh massiv."
    )
    correct_answer = models.TextField(
        blank=True,
        verbose_name= "To'g'ri javob",
        help_text="Single uchun to'g'ri variant. Multiple uchun to'g'ri variantlar massivi. Open uchun matn."
    )
    score = models.PositiveIntegerField(
        default=1,
        verbose_name= 'Ball'
    )
    explanation = models.TextField(
        blank=True,
        verbose_name= 'Tushuntirish'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_questions',
        verbose_name= 'Kim tomonidan yaratilgan'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True,
        verbose_name= 'Faol'
    )

    class Meta:
        verbose_name =  'Imtihon savoli '
        verbose_name_plural = 'Imtihon savollari'
        ordering = ['course', 'id']

    def __str__(self):
        return f"{self.course.code} - Savol #{self.id}"


class ExamResult(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='exam_results',
        verbose_name= 'Tinglovchi'
    )
    question = models.ForeignKey(
        ExamQuestion,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name= 'Savol'
    )
    answer = models.TextField(
        blank=True,
        verbose_name= "Tinglovchining javobi"
    )
    score_obtained = models.PositiveIntegerField(
        default=0,
        verbose_name= 'Olingan ball'
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name= "To'g'ri"
    )
    evaluated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluated_results',
        verbose_name= 'Kim tomonidan baholangan'
    )
    evaluated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name= 'Baholash sanasi'
    )
    attempt_number = models.PositiveSmallIntegerField(
        default=1,
        verbose_name= 'Urinish raqami'
    )
    is_retake = models.BooleanField(
        default=False,
        verbose_name= 'Qayta topshirish'
    )
    approved_by_director = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_retake_results',
        verbose_name= 'Qayta topshirishni tasdiqlagan direktor'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name =  'Imtihon natijasi '
        verbose_name_plural = 'Imtihon natijalari'
        unique_together = ('student', 'question', 'attempt_number')

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.question} - {self.score_obtained}"


class TestSession(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='test_sessions',
        verbose_name= 'Tinglovchi'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='test_sessions',
        verbose_name= 'Kurs'
    )
    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name= 'Boshlanish vaqti'
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name= 'Tugash vaqti'
    )
    total_questions = models.PositiveIntegerField(
        default=0,
        verbose_name= 'Jami savollar'
    )
    correct_answers = models.PositiveIntegerField(
        default=0,
        verbose_name= "To'g'ri javoblar"
    )
    total_score = models.PositiveIntegerField(
        default=0,
        verbose_name= 'Umumiy ball'
    )
    max_score = models.PositiveIntegerField(
        default=0,
        verbose_name= 'Maksimal ball'
    )
    is_passed = models.BooleanField(
        default=False,
        verbose_name= 'Topshirilgan'
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name= 'Yakunlangan'
    )
    passing_score_percentage = models.PositiveIntegerField(
        default=70,
        verbose_name= "O'tish foizi"
    )
    attempt_number = models.PositiveSmallIntegerField(
        default=1,
        verbose_name= 'Urinish raqami'
    )
    is_retake = models.BooleanField(
        default=False,
        verbose_name= 'Qayta topshirish sessiyasi'
    )

    class Meta:
        verbose_name =  'Test sessiyasi '
        verbose_name_plural = 'Test sessiyalari'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.code} ({self.start_time.strftime('%d.%m.%Y %H:%M')})"

    @property
    def score_percentage(self):
        if self.max_score > 0:
            return int((self.total_score / self.max_score) * 100)
        return 0
