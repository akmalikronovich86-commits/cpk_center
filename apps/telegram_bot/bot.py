"""
Telegram bot - O'zbek tilida (lotin alifbosi)
Barcha DB so'rovlar sync_to_async orqali (async xatolardan himoya)
"""
import logging
from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

UNKNOWN = "Noma'lum"


# ============ DB funksiyalar (sync_to_async) ============

@sync_to_async
def db_get_user(telegram_user_id):
    try:
        return User.objects.get(telegram_user_id=telegram_user_id)
    except User.DoesNotExist:
        return None


@sync_to_async
def db_announcements_text():
    from apps.certificates.models import Announcement
    items = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]
    if not items:
        return "📢 Hozircha e'lonlar mavjud emas.\n\n"
    text = "📢 <b>So'nggi e'lonlar:</b>\n\n"
    for ann in items:
        content = ann.content[:200] + ('...' if len(ann.content) > 200 else '')
        text += f"<b>{ann.title}</b>\n{content}\n"
        text += f"📅 {ann.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    return text


@sync_to_async
def db_schedule_text(user):
    if user.role != 'student':
        return "ℹ️ Dars jadvali faqat talabalar uchun mavjud.\n\n"
    from apps.groups.models import StudentRecord
    from apps.schedules.models import Schedule
    try:
        record = StudentRecord.objects.get(user=user)
    except StudentRecord.DoesNotExist:
        return "⚠️ Sizning guruhingiz topilmadi.\n\n"
    schedules = Schedule.objects.filter(group=record.group).order_by('date', 'start_time')[:10]
    if not schedules:
        return "📅 Sizning guruhingiz uchun dars jadvali mavjud emas.\n\n"
    text = f"📅 <b>Guruhingiz jadvali ({record.group}):</b>\n\n"
    for sch in schedules:
        module_name = getattr(getattr(sch, 'module', None), 'name', 'Dars') or 'Dars'
        lecturer = getattr(sch, 'lecturer', None)
        lecturer_name = getattr(getattr(lecturer, 'user', None), 'full_name', UNKNOWN) or UNKNOWN
        text += f"📚 {module_name}\n"
        text += f"📅 {sch.date.strftime('%d.%m.%Y')}\n"
        text += f"🕐 {sch.start_time.strftime('%H:%M')} - {sch.end_time.strftime('%H:%M')}\n"
        text += f"👨‍ {lecturer_name}\n\n"
    return text


@sync_to_async
def db_certificates_text(user):
    from apps.groups.models import StudentRecord
    from apps.certificates.models import Certificate
    try:
        record = StudentRecord.objects.get(user=user)
    except StudentRecord.DoesNotExist:
        return "⚠️ Sizning talaba profilingiz topilmadi.\n\n"
    certs = Certificate.objects.filter(student=record, status='issued').order_by('-issue_date')
    if not certs:
        return "🎓 Sizda hali sertifikatlar mavjud emas.\n\n"
    text = "🎓 <b>Sizning sertifikatlar:</b>\n\n"
    for cert in certs:
        text += f"📜 Sertifikat #{cert.certificate_number}\n"
        text += f"📅 Berilgan sana: {cert.issue_date.strftime('%d.%m.%Y')}\n"
        text += f"✅ Holat: {cert.get_status_display()}\n\n"
    return text


# ============ Handlers ============

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 E'lonlar", callback_data='announcements')],
        [InlineKeyboardButton("📅 Dars jadvali", callback_data='schedule')],
        [InlineKeyboardButton("🎓 Sertifikatlarim", callback_data='certificates')],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data='help')],
    ])


def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Orqaga", callback_data='back_to_menu')]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botni boshlash"""
    telegram_user_id = update.effective_user.id
    username = update.effective_user.username

    user = await db_get_user(telegram_user_id)
    if user:
        name = user.full_name or user.username
        await update.message.reply_text(
            f"Assalomu alaykum, {name}! 👋\n\n"
            f"Siz allaqachon ro'yxatdan o'tgansiz.\n\n"
            f"/menu - Asosiy menyu"
        )
    else:
        await update.message.reply_text(
            f"Assalomu alaykum! 👋\n\n"
            f"Sizning Telegram ID: <b>{telegram_user_id}</b>\n"
            f"Username: @{username or 'mavjud emas'}\n\n"
            f"⚠️ Diqqat: Tizimda ro'yxatdan o'tish uchun administrator bilan bog'laning.\n"
            f"Yuqoridagi ID raqamini administratorga yuboring.",
            parse_mode='HTML'
        )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asosiy menyu"""
    user = await db_get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "⚠️ Siz tizimda ro'yxatdan o'tmagansiz.\n"
            "Avval /start buyrug'ini yuboring va administrator bilan bog'laning."
        )
        return
    name = user.full_name or user.username
    await update.message.reply_text(
        f"Assalomu alaykum, {name}! 👋\n\n"
        f"Quyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu_keyboard()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalar"""
    query = update.callback_query
    await query.answer()

    user = await db_get_user(update.effective_user.id)
    if not user:
        await query.edit_message_text("⚠️ Siz tizimda ro'yxatdan o'tmagansiz.")
        return

    if query.data == 'announcements':
        text = await db_announcements_text()
    elif query.data == 'schedule':
        text = await db_schedule_text(user)
    elif query.data == 'certificates':
        text = await db_certificates_text(user)
    elif query.data == 'help':
        text = (
            "ℹ️ <b>Botdan qanday foydalanish:</b>\n\n"
            "📢 <b>E'lonlar</b> - Markazdagi so'nggi e'lonlar\n"
            "📅 <b>Dars jadvali</b> - Guruhingiz dars jadvali\n"
            "🎓 <b>Sertifikatlarim</b> - Sertifikatlar ro'yxati\n\n"
            "<b>Buyruqlar:</b>\n"
            "/start - Botni boshlash\n"
            "/menu - Asosiy menyu\n"
            "/help - Yordam\n\n"
            "Savollar bo'lsa, administrator bilan bog'laning."
        )
    elif query.data == 'back_to_menu':
        name = user.full_name or user.username
        await query.edit_message_text(
            f"Assalomu alaykum, {name}! 👋\n\n"
            f"Quyidagi bo'limlardan birini tanlang:",
            reply_markup=main_menu_keyboard()
        )
        return
    else:
        return

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=back_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ <b>Yordam:</b>\n\n"
        "/start - Botni boshlash\n"
        "/menu - Asosiy menyu\n"
        "/help - Yordam\n\n"
        "Savollar bo'lsa, administrator bilan bog'laning.",
        parse_mode='HTML'
    )


def create_bot_application():
    """Bot ilovasini yaratish"""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan. Bot ishlamaydi.")
        return None

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    return application
