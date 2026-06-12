import pytest
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model

from loterias.models import Contest, Game, GameResult
from loterias.services import ResultCalculationService

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="pass")


@pytest.fixture
def contest(db):
    return Contest.objects.create(
        number=3095,
        draw_date=date(2026, 6, 11),
        winning_numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        prize_pool=Decimal("48500000.00"),
        accumulated=False,
    )


@pytest.fixture
def service():
    return ResultCalculationService()


def _make_game(user, numbers: list[int]) -> Game:
    return Game.objects.create(user=user, numbers=numbers)


@pytest.mark.django_db
class TestResultCalculationService:
    def test_hits_calculated_correctly(self, user, contest, service) -> None:
        # 10 acertos: números 1-10 acertam, 16-20 erram
        game = _make_game(user, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 17, 18, 19, 20])
        result = service.calculate(game, contest)
        assert result.hits == 10

    def test_zero_hits(self, user, contest, service) -> None:
        game = _make_game(user, [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 16, 17, 18, 19, 20])
        result = service.calculate(game, contest)
        assert result.hits == 0

    def test_fifteen_hits(self, user, contest, service) -> None:
        game = _make_game(user, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        result = service.calculate(game, contest)
        assert result.hits == 15

    def test_prize_zero_below_11_hits(self, user, contest, service) -> None:
        game = _make_game(user, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 17, 18, 19, 20])
        result = service.calculate(game, contest)
        assert result.hits == 10
        assert result.prize == Decimal("0")

    def test_prize_11_hits(self, user, contest, service) -> None:
        game = _make_game(user, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 19])
        result = service.calculate(game, contest)
        assert result.hits == 11
        assert result.prize == Decimal("6.00")

    def test_prize_12_hits(self, user, contest, service) -> None:
        game = _make_game(user, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18])
        result = service.calculate(game, contest)
        assert result.hits == 12
        assert result.prize == Decimal("12.00")

    def test_prize_13_hits(self, user, contest, service) -> None:
        game = _make_game(user, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17])
        result = service.calculate(game, contest)
        assert result.hits == 13
        assert result.prize == Decimal("25.00")

    def test_prize_14_hits_is_zero_without_rateio(self, user, contest, service) -> None:
        # 14 e 15 acertos dependem do rateio do concurso — armazenado como 0 por ora
        game = _make_game(user, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16])
        result = service.calculate(game, contest)
        assert result.hits == 14
        assert result.prize == Decimal("0")

    def test_result_is_idempotent(self, user, contest, service) -> None:
        # Recalcular não duplica registros
        game = _make_game(user, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        service.calculate(game, contest)
        service.calculate(game, contest)
        assert GameResult.objects.filter(game=game, contest=contest).count() == 1

    def test_calculate_all_for_contest(self, user, contest, service) -> None:
        _make_game(user, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        _make_game(user, [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 1, 2, 3, 4, 5])
        results = service.calculate_all_for_contest(contest)
        assert len(results) == 2

    def test_calculate_all_for_game(self, user, db, service) -> None:
        contest1 = Contest.objects.create(
            number=1, draw_date=date(2003, 9, 29),
            winning_numbers=list(range(1, 16)), accumulated=False,
        )
        contest2 = Contest.objects.create(
            number=2, draw_date=date(2003, 10, 6),
            winning_numbers=list(range(11, 26)), accumulated=False,
        )
        game = _make_game(user, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        results = service.calculate_all_for_game(game)
        assert len(results) == 2
