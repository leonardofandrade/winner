import io
from datetime import date
from decimal import Decimal

import openpyxl
import pytest

from core.exceptions import ParseError
from loterias.parsers import LotofacilXlsParser


def _build_xls(rows: list[tuple]) -> bytes:
    """Cria bytes de um XLSX com cabeçalho + linhas fornecidas."""
    wb = openpyxl.Workbook()
    ws = wb.active
    header = (
        "Concurso", "Data Sorteio",
        "Bola1", "Bola2", "Bola3", "Bola4", "Bola5",
        "Bola6", "Bola7", "Bola8", "Bola9", "Bola10",
        "Bola11", "Bola12", "Bola13", "Bola14", "Bola15",
        "Ganhadores 15 acertos", "Cidade / UF",
        "Rateio 15 acertos", "Ganhadores 14 acertos", "Rateio 14 acertos",
        "Ganhadores 13 acertos", "Rateio 13 acertos",
        "Ganhadores 12 acertos", "Rateio 12 acertos",
        "Ganhadores 11 acertos", "Rateio 11 acertos",
        "Acumulado 15 acertos", "Arrecadacao Total",
        "Estimativa Premio", "Acumulado especial", "Observacao",
    )
    ws.append(header)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _make_row(
    number: int = 1,
    date_str: str = "29/09/2003",
    balls: tuple = (2, 3, 5, 6, 9, 10, 11, 13, 14, 16, 18, 20, 23, 24, 25),
    accumulated_str: str = "R$0,00",
    prize_pool_str: str = "R$49.765,82",
) -> tuple:
    return (
        number, date_str,
        *balls,
        5, "BA; SP",
        "R$49.765,82", 154, "R$689,84",
        4645, "R$10,00",
        48807, "R$4,00",
        257593, "R$2,00",
        accumulated_str, prize_pool_str,
        "R$250.000,00", "R$0,00", None,
    )


@pytest.fixture
def parser() -> LotofacilXlsParser:
    return LotofacilXlsParser()


class TestLotofacilXlsParser:
    def test_parse_all_returns_correct_count(self, parser) -> None:
        data = _build_xls([_make_row(1), _make_row(2)])
        result = parser.parse_all(data)
        assert len(result) == 2

    def test_parse_number(self, parser) -> None:
        data = _build_xls([_make_row(3095)])
        result = parser.parse_all(data)
        assert result[0]["number"] == 3095

    def test_parse_draw_date(self, parser) -> None:
        data = _build_xls([_make_row(1, date_str="29/09/2003")])
        result = parser.parse_all(data)
        assert result[0]["draw_date"] == date(2003, 9, 29)

    def test_parse_winning_numbers_sorted(self, parser) -> None:
        balls = (25, 1, 14, 3, 9, 10, 11, 13, 5, 16, 18, 20, 23, 24, 7)
        data = _build_xls([_make_row(1, balls=balls)])
        result = parser.parse_all(data)
        assert result[0]["winning_numbers"] == sorted(balls)

    def test_parse_winning_numbers_are_integers(self, parser) -> None:
        data = _build_xls([_make_row(1)])
        result = parser.parse_all(data)
        assert all(isinstance(n, int) for n in result[0]["winning_numbers"])

    def test_parse_not_accumulated(self, parser) -> None:
        data = _build_xls([_make_row(1, accumulated_str="R$0,00")])
        result = parser.parse_all(data)
        assert result[0]["accumulated"] is False

    def test_parse_accumulated(self, parser) -> None:
        data = _build_xls([_make_row(1, accumulated_str="R$2.195.593,25")])
        result = parser.parse_all(data)
        assert result[0]["accumulated"] is True

    def test_parse_prize_pool(self, parser) -> None:
        data = _build_xls([_make_row(1, prize_pool_str="R$22.711.636,50")])
        result = parser.parse_all(data)
        assert result[0]["prize_pool"] == Decimal("22711636.50")

    def test_parse_prize_pool_zero_returns_none(self, parser) -> None:
        data = _build_xls([_make_row(1, prize_pool_str="R$0,00")])
        result = parser.parse_all(data)
        assert result[0]["prize_pool"] is None

    def test_empty_row_is_skipped(self, parser) -> None:
        # Linha com número None deve ser ignorada silenciosamente
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(("Concurso", "Data Sorteio", *[f"Bola{i}" for i in range(1, 16)], *["x"] * 16))
        ws.append((None, None, *([None] * 30)))
        buf = io.BytesIO()
        wb.save(buf)
        result = parser.parse_all(buf.getvalue())
        assert result == []

    def test_invalid_bytes_raises_parse_error(self, parser) -> None:
        with pytest.raises(ParseError):
            parser.parse_all(b"not a valid xlsx")
