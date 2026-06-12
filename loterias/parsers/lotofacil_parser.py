from datetime import date, datetime
from typing import TypedDict

from core.exceptions import ParseError

# faixa 1 = 15 acertos, faixa 2 = 14, ..., faixa 5 = 11
_FAIXA_TO_HITS = {1: 15, 2: 14, 3: 13, 4: 12, 5: 11}


class ParsedContest(TypedDict):
    number: int
    draw_date: date
    winning_numbers: list[int]
    prize_pool: float | None
    accumulated: bool
    prize_tiers: dict | None


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
                prize_tiers=self._parse_tiers(raw.get("listaRateioPremio", [])),
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise ParseError(f"Cannot parse contest data: {exc}") from exc

    def _parse_tiers(self, rateio_list: list) -> dict | None:
        """Extrai valorPremio por faixa de acertos como dict {hits: str_value}."""
        if not rateio_list:
            return None
        tiers = {}
        for item in rateio_list:
            faixa = item.get("faixa")
            hits = _FAIXA_TO_HITS.get(faixa)
            if hits is not None:
                tiers[str(hits)] = str(item.get("valorPremio", 0))
        return tiers or None

    def _parse_date(self, value: str) -> date:
        return datetime.strptime(value, self._DATE_FORMAT).date()
