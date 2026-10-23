from datetime import date

import pytest
from django.contrib.auth import get_user_model

from loterias.models import Contest, Game, GameResult, GameSet
from telegram_bot.models import TelegramUser
from telegram_bot.services import SimulateWinService

User = get_user_model()

WINNING = [2, 3, 5, 6, 9, 10, 11, 13, 14, 16, 18, 20, 23, 24, 25]


@pytest.fixture
def user(db):
    return User.objects.create_user(username="leo", password="pass")


@pytest.fixture
def tg_user(db, user):
    return TelegramUser.objects.create(telegram_id=174183824, first_name="Leo", user=user)


def _contest(number: int, jackpot: str | None) -> Contest:
    tiers = {"15": jackpot, "14": "1924.65"} if jackpot is not None else None
    return Contest.objects.create(
        number=number, draw_date=date(2026, 10, 20),
        winning_numbers=WINNING, accumulated=False, prize_tiers=tiers,
    )


@pytest.mark.django_db
class TestSimulateWinService:
    def test_returns_none_without_contests(self, tg_user) -> None:
        assert SimulateWinService().execute(tg_user) is None

    def test_uses_users_game_label_and_latest_jackpot(self, tg_user, user) -> None:
        _contest(3808, "1734567.89")
        _contest(3809, "0.0")  # acumulou: busca o rateio do concurso anterior
        game_set = GameSet.objects.create(user=user, name="firma")
        game = Game.objects.create(user=user, game_set=game_set, numbers=list(range(1, 16)))

        text = SimulateWinService().execute(tg_user)

        assert text.startswith("🧪 *Simulação*")
        assert "Concurso #3809" in text
        assert f"Jogo #{game.pk} (firma): *15 acertos* — R$ 1.734.567,89" in text

    def test_does_not_persist_anything(self, tg_user, user) -> None:
        _contest(3809, "1000000.00")
        Game.objects.create(user=user, numbers=list(range(1, 16)))
        SimulateWinService().execute(tg_user)
        assert GameResult.objects.count() == 0
        assert Game.objects.get().numbers == list(range(1, 16))

    def test_works_without_linked_account(self, db) -> None:
        _contest(3809, None)
        text = SimulateWinService().execute(None)
        assert "Jogo #1: *15 acertos* — R$ 1.500.000,00" in text
