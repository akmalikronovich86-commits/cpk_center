"""
Telegram bot asosiy fayli - O'zbek tilida (lotin alifbosi)
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.certificates.models import Announcement
from apps.schedules.models import Schedule
from apps.certificates.models import Certificate

logger = logging.getLogger(__name__)
User = get_user_model()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botni boshlash va foydalanuvchini ro'yxatdan o'tkazish"""
    telegram_user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Foydalanuvchini qidiramiz
    try:
        user = User.objects.get(telegram_user_id=telegram_user_id)
        await update.message.reply_text(
            f"Assalomu alaykum, {user.full_name or user.username}! 👋\n\n"
            f"Siz allaqachon ro'yxatdan o'tgansiz.\n\n"
            f"/menu - Asosiy menyu"
        )
    except User.DoesNotExist:
        await update.message.reply_text(
            f"Assalomu alaykum! 👋\n\n"
            f"Sizning Telegram ID: {telegram_user_id}\n"
            f"Username: @{username or 'mavjud emas'}\n\n"
            f"⚠️ Diqqat: Tizimda ro'yxatdan o'tish uchun administrator bilan bog'laning.\n"
            f"Sizning Telegram ID raqamingizni administratorga yuboring."
        )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asosiy menyu"""
    telegram_user_id = update.effective_user.id
    
    try:
        user = User.objects.get(telegram_user_id=telegram_user_id)
    except User.DoesNotExist:
        await update.message.reply_text(
            "⚠️ Siz tizimda ro'yxatdan o'tmagansiz.\n"
            "Administrator bilan bog'laning."
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("📢 E'lonlar", callback_data='announcements')],
        [InlineKeyboardButton("📅 Dars jadvali", callback_data='schedule')],
        [InlineKeyboardButton("🎓 Sertifikatlarim", callback_data='certificates')],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Assalomu alaykum, {user.full_name or user.username}! 👋\n\n"
        f"Quyidagi bo'limlardan birini tanlang:",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalarni bosishni boshqarish"""
    query = update.callback_query
    await query.answer()
    
    telegram_user_id = update.effective_user.id
    
    try:
        user = User.objects.get(telegram_user_id=telegram_user_id)
    except User.DoesNotExist:
        await query.edit_message_text("⚠️ Siz tizimda ro'yxatdan o'tmagansiz.")
        return
    
    if query.data == 'announcements':
        await show_announcements(query, user)
    elif query.data == 'schedule':
        await show_schedule(query, user)
    elif query.data == 'certificates':
        await show_certificates(query, user)
    elif query.data == 'help':
        await show_help(query)
    elif query.data == 'back_to_menu':
        await back_to_menu(query, user)


async def show_announcements(query, user):
    """E'lonlarni ko'rsatish"""
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    if not announcements:
        text = "📢 Hozircha e'lonlar mavjud emas.\n\n"
    else:
        text = "📢 <b>So'nggi e'lonlar:</b>\n\n"
        for ann in announcements:
            text += f"<b>{ann.title}</b>\n"
            text += f"{ann.content[:200]}{'...' if len(ann.content) > 200 else ''}\n"
            text += f"📅 {ann.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    
    keyboard = [[InlineKeyboardButton("◀️ Orqaga", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def show_schedule(query, user):
    """Dars jadvalini ko'rsatish"""
    # Agar talaba bo'lsa, o'z guruhining jadvalini ko'rsatamiz
    if user.role == 'student':
        from apps.groups.models import StudentRecord
        try:
            student_record = StudentRecord.objects.get(user=user)
            schedules = Schedule.objects.filter(
                group=student_record.group
            ).order_by('date', 'start_time')[:10]
            
            if not schedules:
                text = "📅 Sizning guruhingiz uchun dars jadvali mavjud emas.\n\n"
            else:
                text = f"📅 <b>Sizning guruhingiz jadvali ({student_record.group}):</b>\n\n"
                for schedule in schedules:
                    text += f"📚 {schedule.module.name if schedule.module else 'Dars'}\n"
                    text += f"📅 {schedule.date.strftime('%d.%m.%Y')}\n"
                    text += f"🕐 {schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}\n"
                    text += f"👨‍🏫 {schedule.lecturer.user.full_name if schedule.lecturer else 'Noma\\'lum'}\n\n"
        except StudentRecord.DoesNotExist:
            text = "⚠️ Sizning guruhingiz topilmadi.\n\n"
    else:
        text = "ℹ️ Dars jadvali faqat talabalar uchun mavjud.\n\n"
    
    keyboard = [[InlineKeyboardButton("◀️ Orqaga", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def show_certificates(query, user):
    """Sertifikatlarni ko'rsatish"""
    from apps.groups.models import StudentRecord
    
    try:
        student_record = StudentRecord.objects.get(user=user)
        certificates = Certificate.objects.filter(
            student=student_record,
            status='issued'
        ).order_by('-issue_date')
        
        if not certificates:
            text = "🎓 Sizda hali sertifikatlar mavjud emas.\n\n"
        else:
            text = "🎓 <b>Sizning sertifikatlar:</b>\n\n"
            for cert in certificates:
                text += f"📜 Sertifikat #{cert.certificate_number}\n"
                text += f"📅 Berilgan sana: {cert.issue_date.strftime('%d.%m.%Y')}\n"
                text += f"✅ Holat: {cert.get_status_display()}\n\n"
    except StudentRecord.DoesNotExist:
        text = "⚠️ Sizning talaba profilingiz topilmadi.\n\n"
    
    keyboard = [[InlineKeyboardButton("◀️ Orqaga", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def show_help(query):
    """Yordam ko'rsatish"""
    text = (
        "ℹ️ <b>Botdan qanday foydalanish:</b>\n\n"
        "📢 <b>E'lonlar</b> - Markazdagi so'nggi e'lonlarni ko'rish\n\n"
        "📅 <b>Dars jadvali</b> - O'z guruhingizning dars jadvalini ko'rish\n\n"
        "🎓 <b>Sertifikatlarim</b> - O'z sertifikatlar ro'yxatini ko'rish\n\n"
        "<b>Buyruqlar:</b>\n"
        "/start - Botni qayta ishga tushirish\n"
        "/menu - Asosiy menyu\n"
        "/help - Yordam\n\n"
        "Savollar bo'lsa, administrator bilan bog'laning."
    )
    
    keyboard = [[InlineKeyboardButton("◀️ Orqaga", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def back_to_menu(query, user):
    """Asosiy menyuga qaytish"""
    keyboard = [
        [InlineKeyboardButton("📢 E'lonlar", callback_data='announcements')],
        [InlineKeyboardButton("📅 Dars jadvali", callback_data='schedule')],
        [InlineKeyboardButton("🎓 Sertifikatlarim", callback_data='certificates')],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"Assalomu alaykum, {user.full_name or user.username}! 👋\n\n"
        f"Quyidagi bo'limlardan birini tanlang:",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam buyrug'i"""
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
    
    # Buyruqlarni ro'yxatdan o'tkazish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("help", help_command))
    
    # Tugmalarni bosishni boshqarish
    application.add_handler(CallbackQueryHandler(button_handler))
    
    return application
