import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Bot

from telegram_bot.services import DailyReportService


async def _run() -> int:
    async with Bot(token=settings.TELEGRAM_BOT_TOKEN) as bot:
        return await DailyReportService().run(bot)


class Command(BaseCommand):
    help = "Sync Lotofacil contests and send pending prize notifications via Telegram"

    def handle(self, *args, **options) -> None:
        sent = asyncio.run(_run())
        self.stdout.write(self.style.SUCCESS(f"Daily report sent: {sent} contest notifications."))
