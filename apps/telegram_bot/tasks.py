"""
Celery vazifalari - Telegram xabarlarini HTTP API orqali yuborish
"""
import logging
import requests
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def _send_message(chat_id, text):
    """Telegram HTTP API orqali xabar yuborish (sync, Celery uchun xavfsiz)"""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan")
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Xabar yuborishda xatolik: {e}")
        return False


@shared_task
def send_announcement_to_all(announcement_id):
    """Yangi e'lonni barcha bog'langan foydalanuvchilarga yuborish"""
    from apps.certificates.models import Announcement
    try:
        announcement = Announcement.objects.get(id=announcement_id)
    except Announcement.DoesNotExist:
        logger.error(f"E'lon {announcement_id} topilmadi")
        return 0

    message = (
        f"📢 <b>Yangi e'lon!</b>\n\n"
        f"<b>{announcement.title}</b>\n\n"
        f"{announcement.content}\n\n"
        f"📅 {announcement.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Batafsil: /menu"
    )

    sent = 0
    for user in User.objects.filter(telegram_user_id__isnull=False):
        if _send_message(user.telegram_user_id, message):
            sent += 1
    logger.info(f"E'lon {announcement_id}: {sent} ta xabar yuborildi")
    return sent


@shared_task
def send_certificate_ready(certificate_id):
    """Sertifikat tayyor bo'lganda talabaga xabar"""
    from apps.certificates.models import Certificate
    try:
        certificate = Certificate.objects.get(id=certificate_id)
        user = certificate.student.user
    except (Certificate.DoesNotExist, AttributeError):
        logger.error(f"Sertifikat {certificate_id} topilmadi")
        return

    if not user.telegram_user_id:
        logger.warning(f"User {user.id} Telegram bilan bog'lanmagan")
        return

    course_name = getattr(getattr(certificate, 'course', None), 'name', "Noma'lum") or "Noma'lum"
    message = (
        f"🎉 <b>Tabriklaymiz!</b>\n\n"
        f"Sizning sertifikatingiz tayyor!\n\n"
        f"📜 Raqam: <b>{certificate.certificate_number}</b>\n"
        f"📅 Sana: {certificate.issue_date.strftime('%d.%m.%Y')}\n"
        f"📚 Kurs: {course_name}\n\n"
        f"Yuklab olish uchun shaxsiy kabinetingizga kiring.\n/menu"
    )
    if _send_message(user.telegram_user_id, message):
        logger.info(f"Sertifikat {certificate_id} xabari yuborildi")


@shared_task
def send_schedule_reminder(schedule_id):
    """Darsdan 1 soat oldin guruh talabalariga eslatma"""
    from apps.schedules.models import Schedule
    from apps.groups.models import StudentRecord
    try:
        schedule = Schedule.objects.get(id=schedule_id)
    except Schedule.DoesNotExist:
        logger.error(f"Jadval {schedule_id} topilmadi")
        return 0

    module_name = getattr(getattr(schedule, 'module', None), 'name', 'Dars') or 'Dars'
    lecturer = getattr(schedule, 'lecturer', None)
    lecturer_name = getattr(getattr(lecturer, 'user', None), 'full_name', "Noma'lum") or "Noma'lum"

    message = (
        f"⏰ <b>Dars eslatmasi!</b>\n\n"
        f"📚 {module_name}\n"
        f"📅 {schedule.date.strftime('%d.%m.%Y')}\n"
        f"🕐 {schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}\n"
        f"👨‍🏫 {lecturer_name}\n\n"
        f"Dars tez orada boshlanadi!"
    )

    sent = 0
    for student in StudentRecord.objects.filter(group=schedule.group):
        tg_id = getattr(getattr(student, 'user', None), 'telegram_user_id', None)
        if tg_id and _send_message(tg_id, message):
            sent += 1
    logger.info(f"Jadval {schedule_id}: {sent} ta eslatma yuborildi")
    return sent
