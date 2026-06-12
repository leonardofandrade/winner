from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from django.contrib.auth import get_user_model

from loterias.models import Contest, Game, GameResult
from telegram_bot.models import TelegramUser
from telegram_bot.services.notify_results_service import NotifyResultsService, _fmt_brl

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="leo", password="pass")


@pytest.fixture
def tg_user(db, user):
    return TelegramUser.objects.create(telegram_id=174183824, username="leo", first_name="Leo", user=user)


@pytest.fixture
def contest(db):
    return Contest.objects.create(
        number=3709, draw_date=date(2026, 6, 16),
        winning_numbers=list(range(1, 16)), accumulated=False,
    )


@pytest.fixture
def game(db, user):
    return Game.objects.create(user=user, numbers=list(range(1, 16)))


class TestFmtBrl:
    def test_formats_simple(self) -> None:
        assert _fmt_brl(Decimal("6.00")) == "R$ 6,00"

    def test_formats_thousands(self) -> None:
        assert _fmt_brl(Decimal("1234.50")) == "R$ 1.234,50"

    def test_formats_zero(self) -> None:
        assert _fmt_brl(Decimal("0")) == "R$ 0,00"


@pytest.mark.django_db
class TestNotifyResultsService:
    def test_build_message_with_prize(self, contest, game) -> None:
        result = GameResult(game=game, contest=contest, hits=13, prize=Decimal("25.00"))
        service = NotifyResultsService()
        msg = service._build_message(contest, [(game, result)])
        assert "3709" in msg
        assert "13 acertos" in msg
        assert "R$ 25,00" in msg

    def test_build_message_no_prize(self, contest, game) -> None:
        result = GameResult(game=game, contest=contest, hits=9, prize=Decimal("0"))
        service = NotifyResultsService()
        msg = service._build_message(contest, [(game, result)])
        assert "9 acertos" in msg
        assert "Total" not in msg

    def test_build_message_shows_sorteio(self, contest, game) -> None:
        result = GameResult(game=game, contest=contest, hits=15, prize=Decimal("100.00"))
        service = NotifyResultsService()
        msg = service._build_message(contest, [(game, result)])
        assert "01" in msg
        assert "15" in msg

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_notify_contest_skips_users_without_games(self, tg_user, contest) -> None:
        service = NotifyResultsService()
        with patch("telegram_bot.services.notify_results_service.Bot") as MockBot:
            mock_bot = AsyncMock()
            MockBot.return_value.__aenter__ = AsyncMock(return_value=mock_bot)
            MockBot.return_value.__aexit__ = AsyncMock(return_value=False)
            await service.notify_contest(contest)
            mock_bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_notify_contest_sends_message(self, tg_user, contest, game) -> None:
        service = NotifyResultsService()
        with patch("telegram_bot.services.notify_results_service.Bot") as MockBot:
            mock_bot = AsyncMock()
            MockBot.return_value.__aenter__ = AsyncMock(return_value=mock_bot)
            MockBot.return_value.__aexit__ = AsyncMock(return_value=False)
            await service.notify_contest(contest)
            mock_bot.send_message.assert_called_once()
            call_kwargs = mock_bot.send_message.call_args.kwargs
            assert call_kwargs["chat_id"] == tg_user.telegram_id
            assert "3709" in call_kwargs["text"]
