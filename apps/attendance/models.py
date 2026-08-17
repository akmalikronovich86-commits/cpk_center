"""
Darsga kelishni QR-kod orqali belgilash.
Har bir dars uchun bir martalik token (120 daqiqa amal qiladi).
"""
import secrets
import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone


class AttendanceToken(models.Model):
    schedule = models.ForeignKey(
        'schedules.Schedule',
        on_delete=models.CASCADE,
        related_name='attendance_tokens',
        verbose_name='Dars',
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_used = models.BooleanField(default=False, verbose_name='Ishlatilgan')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='Ishlatilgan vaqt')
    used_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='attended_tokens', verbose_name='Ishlatgan',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    expires_at = models.DateTimeField(verbose_name='Amal qilish muddati')
    secret = models.CharField(max_length=64, default=secrets.token_urlsafe, verbose_name='Maxfiy kalit')

    class Meta:
        verbose_name = "Davomat QR tokeni"
        verbose_name_plural = "Davomat QR tokenlari"
        indexes = [models.Index(fields=['token'])]

    def __str__(self):
        if self.is_used:
            status = 'Ishlatilgan'
        elif self.is_active():
            status = 'Faol'
        else:
            status = "Muddati o'tgan"
        return f"Token #{self.id} - {self.schedule} ({status})"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=120)
        super().save(*args, **kwargs)

    def is_active(self):
        return not self.is_used and self.expires_at > timezone.now()

    def use(self, user):
        if not self.is_active():
            raise ValueError("Token muddati o'tgan yoki ishlatilgan")
        self.is_used = True
        self.used_at = timezone.now()
        self.used_by = user
        self.save(update_fields=['is_used', 'used_at', 'used_by'])
