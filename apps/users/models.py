from django.db import models
from apps.directions.models import Direction
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('director', 'Direktor'),
        ('department_head', "Bo'lim boshlig'i"),
        ('methodist', 'Metodist'),
        ('lecturer', "Ma'ruzachi"),
        ('student', 'Tinglovchi'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', verbose_name= "Rol")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name= "Telefon raqami")
    patronymic = models.CharField(max_length=100, blank=True, null=True, verbose_name= "Otasining ismi")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name= "Lavozimi")
    full_name = models.CharField(max_length=200, blank=True, null=True, verbose_name= "To'liq ismi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name= "Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name= "Yangilangan sana")

    def save(self, *args, **kwargs):
        # Логика синхронизации ФИО (Срабатывает при каждом сохранении)
        fn = (self.first_name or "").strip()
        ln = (self.last_name or "").strip()
        full = (self.full_name or "").strip()

        # Если есть только Full Name -> Разбиваем
        if full and not fn and not ln:
            parts = full.split(None, 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else ""
        
        # Если есть Имя/Фамилия, но нет Full Name -> Собираем
        elif not full and (fn or ln):
            self.full_name = f"{fn} {ln}".strip()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name =  'Avtorizatsiyalangan foydalanuvchi  '
        verbose_name_plural = "Avtorizatsiyadan o'tgan foydalanuvchilar"
        app_label = 'users'

    def __str__(self):
        return self.username


class LecturerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile', verbose_name= "Foydalanuvchi")
    specialization = models.CharField(max_length=200, blank=True, null=True, verbose_name= "Asosiy mutaxassisligi")
    experience_years = models.IntegerField(default=0, verbose_name= "Ish tajribasi (yil)")
    working_hours = models.JSONField(blank=True, null=True, verbose_name= "Ish soatlari")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name= "Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name= "Yangilangan sana")

    class Meta:
        verbose_name =  "Ma'ruzachi profili"
        verbose_name_plural = "Ma'ruzachilar"

    def __str__(self):
        return f"{self.user.username} - {self.specialization or 'Ma\'ruzachi'}"


class Module(models.Model):
    name = models.CharField(max_length=200, verbose_name= 'Modul nomi')
    description = models.TextField(blank=True, null=True, verbose_name= 'Tavsif')
    hours = models.IntegerField(default=0, null=True, blank=True, verbose_name= 'Soatlar')
    
    MODULE_TYPE_CHOICES = [
        ('nazariy', 'Nazariy'),
        ('amaliy', 'Amaliy'),
    ]
    module_type = models.CharField(max_length=10, choices=MODULE_TYPE_CHOICES, default='nazariy', verbose_name= 'Dars turi')
    is_active = models.BooleanField(default=True, verbose_name= 'Faol')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name= 'Yaratilgan sana')
    updated_at = models.DateTimeField(auto_now=True, verbose_name= 'Yangilangan sana')
    
    directions = models.ManyToManyField('directions.Direction', blank=True, verbose_name= "Yo'nalishlar", related_name='modules')
    lecturers = models.ManyToManyField('users.LecturerProfile', blank=True, verbose_name= "Ma'ruzachilar", related_name='taught_modules')

    class Meta:
        verbose_name =  "Modul "
        verbose_name_plural = "Modullar"
        app_label = 'directions'
        db_table = 'directions_module'

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', verbose_name= "Foydalanuvchi")
    sequence_number = models.CharField(max_length=20, blank=True, null=True, verbose_name= "T/R")
    xtm = models.CharField(max_length=50, blank=True, null=True, verbose_name= "XTM")
    full_name_qualification = models.CharField(max_length=200, blank=True, null=True, verbose_name= "Malaka oshiruvchilar (FIO)")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name= "Lavozimi")
    passport = models.CharField(max_length=50, blank=True, null=True, verbose_name= "Pasport")
    birth_date = models.CharField(max_length=50, blank=True, null=True, verbose_name= "Tug'ilgan sana")
    group = models.CharField(max_length=50, blank=True, null=True, verbose_name= "Guruhi")
    regional_branch = models.CharField(max_length=100, blank=True, null=True, verbose_name= "Hududiy filiali nomi")
    district_power_supply = models.CharField(max_length=100, blank=True, null=True, verbose_name= "Tuman elektr ta'minoti")
    phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name= "Telefon raqami")
    final_grade = models.CharField(max_length=50, blank=True, null=True, verbose_name= "Yakuniy bahosi")
    independent_study_topic = models.TextField(blank=True, null=True, verbose_name= "Mustaqil ta'lim mavzusi")
    qualification_period = models.CharField(max_length=50, blank=True, null=True, verbose_name= "Malaka oshirish muddati")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name= "Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name= "Yangilangan sana")

    class Meta:
        verbose_name =  "Tinglovchi profili "
        verbose_name_plural = "Tinglovchilar"

    def __str__(self):
        return f"{self.full_name_qualification or self.user.username} - {self.group or 'Tinglovchi'}"
