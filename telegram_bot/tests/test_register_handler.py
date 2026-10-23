from unittest.mock import AsyncMock, MagicMock

import pytest
from django.contrib.auth import get_user_model

from loterias.models import Game, GameSet
from telegram_bot.handlers.register_handler import ASK_GAMES, registrar_games
from telegram_bot.models import TelegramUser

User = get_user_model()

TELEGRAM_ID = 174183824
GAME_15 = "01 02 03 04 05 06 07 08 09 10 11 12 13 14 15"
GAME_16 = "01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16"


@pytest.fixture
def tg_user(db):
    user = User.objects.create_user(username="leo", password="pass")
    return TelegramUser.objects.create(telegram_id=TELEGRAM_ID, first_name="Leo", user=user)


def _update(text: str) -> MagicMock:
    update = MagicMock()
    update.effective_user.id = TELEGRAM_ID
    update.message.text = text
    update.message.reply_text = AsyncMock()
    return update


def _context() -> MagicMock:
    context = MagicMock()
    context.user_data = {"register_name": "firma", "register_saved": 0}
    return context


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestRegistrarGames:
    async def test_saves_every_line_and_summarizes_by_size(self, tg_user) -> None:
        update, context = _update(f"{GAME_15}\n{GAME_15}\n{GAME_16}"), _context()

        state = await registrar_games(update, context)

        assert state == ASK_GAMES
        assert await Game.objects.filter(game_set__name="firma").acount() == 3
        assert context.user_data["register_saved"] == 3
        reply = update.message.reply_text.call_args.args[0]
        assert "3 jogo(s) salvo(s)" in reply
        assert "2 jogo(s) de 15 dezenas — R$ 3,50 cada" in reply
        assert "1 jogo(s) de 16 dezenas — R$ 56,00 cada" in reply

    async def test_invalid_line_saves_nothing(self, tg_user) -> None:
        update, context = _update(f"{GAME_15}\n1 2 3"), _context()

        state = await registrar_games(update, context)

        assert state == ASK_GAMES
        assert await Game.objects.acount() == 0
        assert not await GameSet.objects.aexists()
        reply = update.message.reply_text.call_args.args[0]
        assert "Linha 2:" in reply and "Nenhum jogo foi salvo" in reply
