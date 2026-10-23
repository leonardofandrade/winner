from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from django.contrib.auth import get_user_model

from loterias.models import Contest, Game, GameResult, GameSet
from telegram_bot.handlers.mygames_handler import mygames_handler
from telegram_bot.models import TelegramUser
from telegram_bot.utils import MESSAGE_LIMIT

User = get_user_model()

TELEGRAM_ID = 174183824


@pytest.fixture
def user(db):
    return User.objects.create_user(username="leo", password="pass")


@pytest.fixture
def tg_user(db, user):
    return TelegramUser.objects.create(telegram_id=TELEGRAM_ID, first_name="Leo", user=user)


def _update() -> MagicMock:
    update = MagicMock()
    update.effective_user.id = TELEGRAM_ID
    update.message.reply_text = AsyncMock()
    return update


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestMygamesHandler:
    async def test_lists_every_game_split_within_telegram_limit(self, tg_user, user) -> None:
        contests = [
            await Contest.objects.acreate(
                number=n, draw_date=date(2026, 10, 1),
                winning_numbers=list(range(1, 16)), accumulated=False,
            )
            for n in range(3800, 3805)
        ]
        game_ids = []
        for set_index in range(3):
            game_set = await GameSet.objects.acreate(user=user, name=f"conjunto-{set_index}")
            for _ in range(10):
                game = await Game.objects.acreate(
                    user=user, game_set=game_set, numbers=list(range(1, 21))
                )
                game_ids.append(game.pk)
                for contest in contests:
                    await GameResult.objects.acreate(
                        game=game, contest=contest, hits=15, prize=Decimal("1000000.00")
                    )

        update = _update()
        await mygames_handler(update, MagicMock())

        chunks = [c.args[0] for c in update.message.reply_text.call_args_list]
        assert len(chunks) > 1
        assert all(len(chunk) <= MESSAGE_LIMIT for chunk in chunks)
        text = "\n".join(chunks)
        assert "Seus jogos (30)" in text
        assert all(f"*Jogo #{pk}*" in text for pk in game_ids)
