from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from loterias.models import Contest, Game, GameResult
from telegram_bot.models import TelegramUser
from telegram_bot.services.notify_results_service import (
    NotifyResultsService,
    _fmt_brl,
)
from telegram_bot.utils import split_message

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


def _make_game(user, created_at: datetime) -> Game:
    game = Game.objects.create(user=user, numbers=list(range(1, 16)))
    # auto_now_add ignora o valor passado no create; ajusta depois
    Game.objects.filter(pk=game.pk).update(created_at=created_at)
    return game


@pytest.fixture
def game(db, user):
    return _make_game(user, datetime(2026, 6, 1, tzinfo=UTC))


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
        msg = service.build_message(contest, [(game, result)])
        assert "3709" in msg
        assert "13 acertos" in msg
        assert "R$ 25,00" in msg

    def test_build_message_no_prize(self, contest, game) -> None:
        result = GameResult(game=game, contest=contest, hits=9, prize=Decimal("0"))
        service = NotifyResultsService()
        msg = service.build_message(contest, [(game, result)])
        assert "9 acertos" in msg
        assert "Total" not in msg

    def test_build_message_shows_sorteio(self, contest, game) -> None:
        result = GameResult(game=game, contest=contest, hits=15, prize=Decimal("100.00"))
        service = NotifyResultsService()
        msg = service.build_message(contest, [(game, result)])
        assert "01" in msg
        assert "15" in msg



class TestSplitMessage:
    def test_short_text_is_single_chunk(self) -> None:
        assert split_message("a\nb") == ["a\nb"]

    def test_long_text_splits_on_lines(self) -> None:
        text = "\n".join("x" * 100 for _ in range(100))
        chunks = split_message(text, limit=1000)
        assert all(len(c) <= 1000 for c in chunks)
        assert "\n".join(chunks) == text


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestNotifyPending:
    async def test_first_run_sends_latest_and_marks_notified(self, tg_user, contest, game) -> None:
        bot = AsyncMock()
        sent = await NotifyResultsService().notify_pending(bot)
        assert sent == 1
        kwargs = bot.send_message.call_args.kwargs
        assert kwargs["chat_id"] == tg_user.telegram_id
        assert "3709" in kwargs["text"]
        await tg_user.arefresh_from_db()
        assert tg_user.last_notified_contest == 3709

    async def test_does_not_resend_notified_contest(self, tg_user, contest, game) -> None:
        bot = AsyncMock()
        service = NotifyResultsService()
        await service.notify_pending(bot)
        sent = await service.notify_pending(bot)
        assert sent == 0
        bot.send_message.assert_called_once()

    async def test_catches_up_missed_contests_in_order(self, tg_user, contest, game) -> None:
        await Contest.objects.acreate(
            number=3708, draw_date=date(2026, 6, 15),
            winning_numbers=list(range(1, 16)), accumulated=False,
        )
        tg_user.last_notified_contest = 3707
        await tg_user.asave()
        bot = AsyncMock()
        sent = await NotifyResultsService().notify_pending(bot)
        assert sent == 2
        texts = [c.kwargs["text"] for c in bot.send_message.call_args_list]
        assert "3708" in texts[0] and "3709" in texts[1]

    async def test_skips_users_without_games_but_marks_notified(self, tg_user, contest) -> None:
        bot = AsyncMock()
        sent = await NotifyResultsService().notify_pending(bot)
        assert sent == 0
        bot.send_message.assert_not_called()
        await tg_user.arefresh_from_db()
        assert tg_user.last_notified_contest == 3709

    async def test_includes_games_registered_after_draw(self, tg_user, user, contest) -> None:
        # Jogos salvos valem para todos os concursos até serem apagados
        await sync_to_async(_make_game)(user, datetime(2026, 6, 20, tzinfo=UTC))
        bot = AsyncMock()
        sent = await NotifyResultsService().notify_pending(bot)
        assert sent == 1

    async def test_send_failure_keeps_contest_pending(self, tg_user, contest, game) -> None:
        bot = AsyncMock()
        bot.send_message.side_effect = RuntimeError("telegram down")
        await NotifyResultsService().notify_pending(bot)
        await tg_user.arefresh_from_db()
        assert tg_user.last_notified_contest is None
