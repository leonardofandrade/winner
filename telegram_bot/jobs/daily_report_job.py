import logging

from asgiref.sync import sync_to_async
from django.db import close_old_connections
from telegram.ext import ContextTypes

from telegram_bot.constants import DAILY_REPORT_MAX_RETRIES, DAILY_REPORT_RETRY_INTERVAL
from telegram_bot.services import DailyReportService

logger = logging.getLogger(__name__)


async def daily_report_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    # À meia-noite a conexão com o MySQL costuma estar parada há horas; descarta antes de usar
    await sync_to_async(close_old_connections)()
    service = DailyReportService()
    await service.run(context.bot)

    if await service.has_yesterdays_draw():
        return
    # O sorteio de ontem ainda não saiu na API da Caixa: agenda nova tentativa
    attempt = context.job.data or 0
    if attempt >= DAILY_REPORT_MAX_RETRIES:
        logger.warning("Daily report: yesterday's draw still missing after %s retries.", attempt)
        return
    logger.info("Daily report: yesterday's draw not published yet, retry %s scheduled.", attempt + 1)
    context.job_queue.run_once(
        daily_report_job,
        when=DAILY_REPORT_RETRY_INTERVAL,
        data=attempt + 1,
        name="daily_report_retry",
    )
