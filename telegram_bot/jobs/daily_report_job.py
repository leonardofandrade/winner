from asgiref.sync import sync_to_async
from django.db import close_old_connections
from telegram.ext import ContextTypes

from telegram_bot.services import DailyReportService


async def daily_report_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    # Às 3h a conexão com o MySQL costuma estar parada há horas; descarta antes de usar
    await sync_to_async(close_old_connections)()
    await DailyReportService().run(context.bot)
