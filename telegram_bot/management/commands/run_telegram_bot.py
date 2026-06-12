from django.core.management.base import BaseCommand

from telegram_bot.runner import run


class Command(BaseCommand):
    help = "Start the Winner Telegram Bot"

    def handle(self, *args, **options) -> None:
        self.stdout.write("Starting Winner Telegram Bot...")
        run()
