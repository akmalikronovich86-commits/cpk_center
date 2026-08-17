"""
Celery vazifalari - Telegram xabarlarini yuborish
"""
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_announcement_to_all(announcement_id):
    """Yangi e'lonni barcha ro'yxatdan o'tgan foydalanuvchilarga yuborish"""
    from apps.certificates.models import Announcement
    from telegram import Bot
    
    try:
        announcement = Announcement.objects.get(id=announcement_id)
    except Announcement.DoesNotExist:
        logger.error(f"E'lon {announcement_id} topilmadi")
        return
    
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan")
        return
    
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    users = User.objects.filter(telegram_user_id__isnull=False)
    
    message = (
        f"📢 <b>Yangi e'lon!</b>\n\n"
        f"<b>{announcement.title}</b>\n\n"
        f"{announcement.content}\n\n"
        f"📅 {announcement.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Batafsil ma'lumot uchun /menu buyrug'ini bosing."
    )
    
    sent_count = 0
    for user in users:
        try:
            bot.send_message(
                chat_id=user.telegram_user_id,
                text=message,
                parse_mode='HTML'
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik (user {user.id}): {e}")
    
    logger.info(f"E'lon {announcement_id} {sent_count} ta foydalanuvchiga yuborildi")
    return sent_count


@shared_task
def send_certificate_ready(certificate_id):
    """Sertifikat tayyor bo'lganda talabaga xabar yuborish"""
    from apps.certificates.models import Certificate
    from telegram import Bot
    
    try:
        certificate = Certificate.objects.get(id=certificate_id)
        user = certificate.student.user
    except (Certificate.DoesNotExist, AttributeError):
        logger.error(f"Sertifikat {certificate_id} yoki foydalanuvchi topilmadi")
        return
    
    if not user.telegram_user_id:
        logger.warning(f"Foydalanuvchi {user.id} Telegram'da ro'yxatdan o'tmagan")
        return
    
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan")
        return
    
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    course_name = certificate.course.name if certificate.course else 'Noma-lum'
    
    message = (
        f"🎉 <b>Tabriklaymiz!</b>\n\n"
        f"Sizning sertifikatingiz tayyor!\n\n"
        f"📜 Sertifikat raqami: <b>{certificate.certificate_number}</b>\n"
        f"📅 Berilgan sana: {certificate.issue_date.strftime('%d.%m.%Y')}\n"
        f"📚 Kurs: {course_name}\n\n"
        f"Sertifikatni yuklab olish uchun shaxsiy kabinetingizga kiring.\n"
        f"/menu - Asosiy menyu"
    )
    
    try:
        bot.send_message(
            chat_id=user.telegram_user_id,
            text=message,
            parse_mode='HTML'
        )
        logger.info(f"Sertifikat {certificate_id} haqida xabar yuborildi")
    except Exception as e:
        logger.error(f"Xabar yuborishda xatolik: {e}")


@shared_task
def send_schedule_reminder(schedule_id):
    """Dars boshlanishidan 1 soat oldin eslatma yuborish"""
    from apps.schedules.models import Schedule
    from apps.groups.models import StudentRecord
    from telegram import Bot
    
    try:
        schedule = Schedule.objects.get(id=schedule_id)
    except Schedule.DoesNotExist:
        logger.error(f"Jadval {schedule_id} topilmadi")
        return
    
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan")
        return
    
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    students = StudentRecord.objects.filter(group=schedule.group)
    
    module_name = schedule.module.name if schedule.module else 'Dars'
    lecturer_name = schedule.lecturer.user.full_name if schedule.lecturer else 'Noma-lum'
    
    message = (
        f"⏰ <b>Dars eslatmasi!</b>\n\n"
        f"📚 {module_name}\n"
        f"📅 Bugun, {schedule.date.strftime('%d.%m.%Y')}\n"
        f"🕐 {schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}\n"
        f"👨‍🏫 {lecturer_name}\n\n"
        f"Dars 1 soatdan keyin boshlanadi!"
    )
    
    sent_count = 0
    for student in students:
        if student.user.telegram_user_id:
            try:
                bot.send_message(
                    chat_id=student.user.telegram_user_id,
                    text=message,
                    parse_mode='HTML'
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Xabar yuborishda xatolik (student {student.id}): {e}")
    
    logger.info(f"Dars eslatmasi {schedule_id} {sent_count} ta talabaga yuborildi")
    return sent_count
