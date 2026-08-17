"""
Telegram botni ishga tushirish buyrug'i
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import asyncio
import logging

from apps.telegram_bot.bot import create_bot_application

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Telegram botni ishga tushirish'

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stderr.write(
                self.style.ERROR(
                    'TELEGRAM_BOT_TOKEN sozlanmagan! '
                    '.env faylida tokenni ko\'rsating.'
                )
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('Telegram bot ishga tushirilmoqda...')
        )
        
        application = create_bot_application()
        if application is None:
            self.stderr.write(
                self.style.ERROR('Bot ilovasini yaratib bo\'lmadi')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(
                'Bot ishga tushdi! To\'xtatish uchun Ctrl+C bosing.'
            )
        )
        
        try:
            application.run_polling(drop_pending_updates=True)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Bot to\'xtatildi')
            )
