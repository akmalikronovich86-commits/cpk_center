from django.db import models
from apps.users.models import User

class KPICategory(models.Model):
    """Категории KPI"""
    name = models.CharField("Nomi", max_length=200)
    description = models.TextField("Tavsif", blank=True)
    max_score = models.DecimalField("Макс. балл", max_digits=5, decimal_places=2, default=0)
    weight = models.IntegerField("Вес", default=1)
    order = models.IntegerField("Порядок", default=0)
    
    class Meta:
        verbose_name = "Категория KPI"
        verbose_name_plural = "Категории KPI"
        ordering = ['order']
    
    def __str__(self):
        return self.name

class KPIIndicator(models.Model):
    """Показатели KPI"""
    category = models.ForeignKey(KPICategory, on_delete=models.CASCADE, related_name='indicators')
    name = models.CharField("Nomi показателя", max_length=300)
    criterion = models.TextField("Критерий оценки")
    max_score = models.DecimalField("Макс. балл", max_digits=5, decimal_places=2)
    measurement_unit = models.CharField("Единица измерения", max_length=50, 
                                          choices=[
                                              ('count', 'Количество'),
                                              ('percent', 'Процент'),
                                              ('date', 'Срок'),
                                              ('boolean', 'Да/Нет')
                                          ])
    target_value = models.DecimalField("Целевое значение", max_digits=10, decimal_places=2, null=True, blank=True)
    deadline = models.DateField("Срок выполнения", null=True, blank=True)
    order = models.IntegerField("Порядок", default=0)
    
    class Meta:
        verbose_name = "Показатель KPI"
        verbose_name_plural = "Показатели KPI"
        ordering = ['category', 'order']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class KPIReport(models.Model):
    """Отчеты по KPI"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kpi_reports')
    period_start = models.DateField("Начало периода")
    period_end = models.DateField("Конец периода")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    total_score = models.DecimalField("Общий балл", max_digits=5, decimal_places=2, default=0)
    status = models.CharField("Holat", max_length=20, 
                              choices=[
                                  ('draft', 'Черновик'),
                                  ('submitted', 'Отправлен'),
                                  ('approved', 'Утвержден'),
                                  ('rejected', 'Отклонен')
                              ], default='draft')
    
    class Meta:
        verbose_name = "Отчет KPI"
        verbose_name_plural = "Отчеты KPI"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Отчет {self.user.get_full_name()} ({self.period_start} - {self.period_end})"

class KPIValue(models.Model):
    """Значения показателей KPI"""
    report = models.ForeignKey(KPIReport, on_delete=models.CASCADE, related_name='kpi_values')
    indicator = models.ForeignKey(KPIIndicator, on_delete=models.CASCADE)
    actual_value = models.DecimalField("Фактическое значение", max_digits=10, decimal_places=2)
    score = models.DecimalField("Полученный балл", max_digits=5, decimal_places=2, default=0)
    evidence = models.TextField("Подтверждение", blank=True)
    attachment = models.FileField("Приложение", upload_to='kpi_attachments/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Значение KPI"
        verbose_name_plural = "Значения KPI"
        unique_together = ['report', 'indicator']
    
    def __str__(self):
        return f"{self.indicator.name}: {self.actual_value}"

class IjroTask(models.Model):
    """Ijro.gov.uz tizimidagi topshiriqlar"""
    task_number = models.CharField("Topshiriq raqami", max_length=100)
    title = models.CharField("Nomi", max_length=500)
    description = models.TextField("Tavsif")
    assigned_by = models.CharField("Kim tomonidan", max_length=200)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ijro_tasks')
    deadline = models.DateField("Bajarish muddati")
    status = models.CharField("Holat", max_length=20,
                              choices=[
                                  ('new', 'Yangi'),
                                  ('in_progress', 'Jarayonda'),
                                  ('completed', 'Bajarildi'),
                                  ('overdue', "Muddati o'tgan")
                              ], default='new')
    created_at = models.DateTimeField("Qabul qilingan sana", auto_now_add=True)
    completed_at = models.DateTimeField("Bajarilgan sana", null=True, blank=True)
    result = models.TextField("Bajarilish natijasi", blank=True)
    incoming_file = models.FileField("Kiruvchi hujjat fayli", upload_to='ijro_tasks/incoming/', null=True, blank=True)
    completed_file = models.FileField("Bajarilgan topshiriq fayli", upload_to='ijro_tasks/completed/', null=True, blank=True)
    
    class Meta:
        verbose_name = "Ijro.gov.uz topshiriqlari"
        verbose_name_plural = "Ijro.gov.uz topshiriqlari"
        ordering = ['deadline', 'status']
    
    def __str__(self):
        return f"{self.task_number} - {self.title}"
