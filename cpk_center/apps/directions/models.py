from django.db import models


class Direction(models.Model):
    name = models.CharField("Yo'nalish nomi", max_length=200)
    code = models.CharField("Kodi", max_length=50, unique=True)
    description = models.TextField("Tavsif", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Yo'nalish "
        verbose_name_plural = "Yo'nalishlar"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

class StudyProgram(models.Model):
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, verbose_name="Yo'nalish", related_name="programs")
    name = models.CharField("Dastur nomi", max_length=300)
    academic_year = models.CharField("Oquv yili", max_length=20, blank=True)
    file = models.FileField("Fayl (PDF/DOCX)", upload_to="programs/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "O'quv dasturi "
        verbose_name_plural = "O'quv dasturlari"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.direction.name}"
