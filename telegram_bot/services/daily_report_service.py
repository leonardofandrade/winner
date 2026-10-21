import logging

from telegram import Bot

from loterias.services import ImportLotofacilService
from telegram_bot.services.notify_results_service import NotifyResultsService

logger = logging.getLogger(__name__)


class DailyReportService:
    """Atualiza a base de concursos e envia aos usuários os prêmios dos concursos novos."""

    def __init__(self) -> None:
        self._import = ImportLotofacilService()
        self._notify = NotifyResultsService()

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
