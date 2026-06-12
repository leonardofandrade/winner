import pytest
from datetime import date

from core.exceptions import ParseError
from loterias.parsers import LotofacilParser
from loterias.tests.fixtures import CONTEST_3095_RAW, CONTEST_ACCUMULATED_RAW


@pytest.fixture
def parser() -> LotofacilParser:
    return LotofacilParser()


class TestLotofacilParser:
    def test_parse_number(self, parser: LotofacilParser) -> None:
        result = parser.parse(CONTEST_3095_RAW)
        assert result["number"] == 3095

    def test_parse_draw_date(self, parser: LotofacilParser) -> None:
        result = parser.parse(CONTEST_3095_RAW)
        assert result["draw_date"] == date(2026, 6, 11)

    def test_parse_winning_numbers_sorted(self, parser: LotofacilParser) -> None:
        result = parser.parse(CONTEST_3095_RAW)
        assert result["winning_numbers"] == sorted(result["winning_numbers"])
        assert len(result["winning_numbers"]) == 15

    def test_parse_winning_numbers_are_integers(self, parser: LotofacilParser) -> None:
        result = parser.parse(CONTEST_3095_RAW)
        assert all(isinstance(n, int) for n in result["winning_numbers"])

    def test_parse_prize_pool(self, parser: LotofacilParser) -> None:
        result = parser.parse(CONTEST_3095_RAW)
        assert result["prize_pool"] == 48_500_000.00

    def test_parse_accumulated_false(self, parser: LotofacilParser) -> None:
        result = parser.parse(CONTEST_3095_RAW)
        assert result["accumulated"] is False

    def test_parse_accumulated_true(self, parser: LotofacilParser) -> None:
        result = parser.parse(CONTEST_ACCUMULATED_RAW)
        assert result["accumulated"] is True

    def test_parse_missing_required_field_raises(self, parser: LotofacilParser) -> None:
        # Sem o campo 'numero' o parser deve lançar ParseError
        raw = {**CONTEST_3095_RAW}
        del raw["numero"]
        with pytest.raises(ParseError):
            parser.parse(raw)

    def test_parse_invalid_date_raises(self, parser: LotofacilParser) -> None:
        raw = {**CONTEST_3095_RAW, "dataApuracao": "2026-06-11"}
        with pytest.raises(ParseError):
            parser.parse(raw)

    def test_parse_missing_prize_pool_returns_none(self, parser: LotofacilParser) -> None:
        raw = {k: v for k, v in CONTEST_3095_RAW.items() if k != "valorArrecadado"}
        result = parser.parse(raw)
        assert result["prize_pool"] is None
