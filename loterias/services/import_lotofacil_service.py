import logging

from asgiref.sync import sync_to_async

from loterias.clients import LotofacilClient
from loterias.models import Contest
from loterias.parsers import LotofacilParser, LotofacilXlsParser
from loterias.repositories import ContestRepository

logger = logging.getLogger(__name__)


class ImportLotofacilService:
    """Orquestra client → parser → repository para importar concursos da Caixa."""

    def __init__(self) -> None:
        self._client = LotofacilClient()
        self._parser = LotofacilParser()
        self._xls_parser = LotofacilXlsParser()
        self._repository = ContestRepository()

    async def import_contest(self, number: int | None = None) -> Contest:
        """Importa um concurso pelo número, ou o mais recente se number for None."""
        raw = await self._client.fetch_contest(number)
        parsed = self._parser.parse(raw)
        contest, created = await sync_to_async(self._repository.update_or_create)(parsed)
        action = "created" if created else "updated"
        logger.info("Contest #%s %s.", parsed["number"], action)
        return contest

    async def import_all_from_xls(self, xls_bytes: bytes) -> int:
        """Importa o histórico completo a partir de bytes de um XLSX da Caixa."""
        parsed_list = self._xls_parser.parse_all(xls_bytes)
        total = await sync_to_async(self._repository.bulk_update_or_create)(parsed_list)
        logger.info("Bulk import finished: %s contests processed.", total)
        return total

    async def import_range(self, start: int, end: int) -> list[Contest]:
        """Importa concursos de start até end (inclusive), ignorando falhas individuais."""
        results: list[Contest] = []
        for number in range(start, end + 1):
            try:
                contest = await self.import_contest(number)
                results.append(contest)
            except Exception:
                logger.exception("Failed to import contest #%s — skipping.", number)
        return results

    async def sync(self) -> tuple[int, int]:
        """
        Detecta gap entre banco e API e importa apenas os concursos faltantes.
        Retorna (latest_number, imported_count).
        """
        latest_in_db = await sync_to_async(self._repository.get_latest_number)()
        raw_latest = await self._client.fetch_contest(None)
        latest_from_api = int(raw_latest["numero"])

        if latest_in_db is None:
            # Banco vazio — importa só o mais recente como ponto de partida
            contest = await self.import_contest(None)
            logger.info("Empty DB: imported latest contest #%s.", contest.number)
            return (contest.number, 1)

        if latest_from_api <= latest_in_db:
            logger.info("Already up to date at contest #%s.", latest_in_db)
            return (latest_in_db, 0)

        contests = await self.import_range(latest_in_db + 1, latest_from_api)
        logger.info("Sync complete: imported %s contests (up to #%s).", len(contests), latest_from_api)
        return (latest_from_api, len(contests))
