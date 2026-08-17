"""
Django signallari - avtomatik xabar yuborish
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender='certificates.Announcement')
def send_announcement_notification(sender, instance, created, **kwargs):
    """Yangi e'lon yaratilganda avtomatik xabar yuborish"""
    if created and instance.is_active:
        if settings.TELEGRAM_BOT_TOKEN:
            from apps.telegram_bot.tasks import send_announcement_to_all
            send_announcement_to_all.delay(instance.id)
            logger.info(f"E'lon {instance.id} uchun xabar yuborish vazifasi qo'shildi")


@receiver(post_save, sender='certificates.Certificate')
def send_certificate_notification(sender, instance, created, **kwargs):
    """Sertifikat yaratilganda yoki holati o'zgarganda xabar yuborish"""
    # Faqat yangi sertifikat yoki holat 'issued' bo'lganda
    if instance.status == 'issued':
        if created or kwargs.get('update_fields'):
            if settings.TELEGRAM_BOT_TOKEN:
                from apps.telegram_bot.tasks import send_certificate_ready
                send_certificate_ready.delay(instance.id)
                logger.info(f"Sertifikat {instance.id} uchun xabar yuborish vazifasi qo'shildi")
