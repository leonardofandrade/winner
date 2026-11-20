import logging
from datetime import date, datetime, timedelta

from asgiref.sync import sync_to_async
from telegram import Bot

from loterias.repositories import ContestRepository
from loterias.services import ImportLotofacilService
from telegram_bot.constants import BOT_TIMEZONE
from telegram_bot.services.notify_results_service import NotifyResultsService

logger = logging.getLogger(__name__)


class DailyReportService:
    """Atualiza a base de concursos e envia aos usuários os prêmios dos concursos novos."""

    def __init__(self) -> None:
        self._import = ImportLotofacilService()
        self._notify = NotifyResultsService()
        self._contests = ContestRepository()

    async def run(self, bot: Bot) -> int:
        """Executa o relatório diário. Retorna o total de mensagens de concurso enviadas."""
        try:
            await self._import.sync()
        except Exception:
            # API da Caixa fora do ar: notifica o que já estiver no banco
            logger.exception("Daily report: contest sync failed.")
        sent = await self._notify.notify_pending(bot)
        logger.info("Daily report finished: %s contest notifications sent.", sent)
        return sent

    async def has_yesterdays_draw(self, today: date | None = None) -> bool:
        """Indica se o concurso sorteado ontem já está no banco (há sorteio todo dia)."""
        today = today or datetime.now(BOT_TIMEZONE).date()
        latest = await sync_to_async(self._contests.get_latest)()
        return latest is not None and latest.draw_date >= today - timedelta(days=1)
