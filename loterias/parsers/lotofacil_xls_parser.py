import io
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import openpyxl

from core.exceptions import ParseError
from loterias.parsers.lotofacil_parser import ParsedContest

# Índices das colunas (0-based) conforme layout do XLSX da Caixa
_COL_NUMBER = 0
_COL_DATE = 1
_COL_BOLA_FIRST = 2   # Bola1
_COL_BOLA_LAST = 16   # Bola15 (inclusive)
_COL_ACCUMULATED = 28  # Acumulado 15 acertos
_COL_PRIZE_POOL = 29   # Arrecadacao Total


def _parse_brl(value: str | None) -> Decimal | None:
    """Converte 'R$22.711.636,50' para Decimal, ou None se vazio/zero."""
    if not value:
        return None
    cleaned = str(value).replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        result = Decimal(cleaned)
        return result if result > 0 else None
    except InvalidOperation:
        return None


class LotofacilXlsParser:
    """Converte bytes de um XLSX da Caixa em list[ParsedContest]."""

    def parse_all(self, data: bytes) -> list[ParsedContest]:
        try:
            # read_only=True quebra com arquivos da Caixa (max_row reportado como 1)
            wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
            ws = wb.active
            results: list[ParsedContest] = []
            for row in ws.iter_rows(min_row=2, values_only=True):  # pula cabeçalho
                parsed = self._parse_row(row)
                if parsed is not None:
                    results.append(parsed)
            wb.close()
            return results
        except Exception as exc:
            raise ParseError(f"Cannot parse XLS data: {exc}") from exc

    def _parse_row(self, row: tuple) -> ParsedContest | None:
        # Linha vazia ou sem número de concurso → ignora
        if not row[_COL_NUMBER]:
            return None
        try:
            winning_numbers = sorted(
                int(row[i]) for i in range(_COL_BOLA_FIRST, _COL_BOLA_LAST + 1)
            )
            return ParsedContest(
                number=int(row[_COL_NUMBER]),
                draw_date=self._parse_date(row[_COL_DATE]),
                winning_numbers=winning_numbers,
                prize_pool=_parse_brl(row[_COL_PRIZE_POOL]),
                accumulated=_parse_brl(row[_COL_ACCUMULATED]) is not None,
            )
        except (TypeError, ValueError) as exc:
            raise ParseError(f"Cannot parse row {row[_COL_NUMBER]}: {exc}") from exc

    def _parse_date(self, value) -> date:
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%d/%m/%Y").date()
