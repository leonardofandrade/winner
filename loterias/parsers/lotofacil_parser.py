from datetime import date, datetime
from typing import TypedDict

from core.exceptions import ParseError


class ParsedContest(TypedDict):
    number: int
    draw_date: date
    winning_numbers: list[int]
    prize_pool: float | None
    accumulated: bool


class LotofacilParser:
    """Converte o JSON bruto da API da Caixa em ParsedContest."""

    _DATE_FORMAT = "%d/%m/%Y"

    def parse(self, raw: dict) -> ParsedContest:
        try:
            return ParsedContest(
                number=int(raw["numero"]),
                draw_date=self._parse_date(raw["dataApuracao"]),
                # Ordena as dezenas para facilitar comparações futuras
                winning_numbers=sorted(int(n) for n in raw["listaDezenas"]),
                prize_pool=raw.get("valorArrecadado"),
                accumulated=bool(raw.get("acumulado", False)),
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise ParseError(f"Cannot parse contest data: {exc}") from exc

    def _parse_date(self, value: str) -> date:
        return datetime.strptime(value, self._DATE_FORMAT).date()
