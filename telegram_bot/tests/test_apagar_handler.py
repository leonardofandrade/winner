from unittest.mock import AsyncMock, MagicMock

import pytest
from django.contrib.auth import get_user_model

from loterias.models import Game, GameSet
from telegram_bot.handlers.apagar_handler import CALLBACK_PREFIX, apagar_confirm, apagar_handler
from telegram_bot.models import TelegramUser

User = get_user_model()

TELEGRAM_ID = 174183824


@pytest.fixture
def user(db):
    return User.objects.create_user(username="leo", password="pass")


@pytest.fixture
def tg_user(db, user):
    return TelegramUser.objects.create(telegram_id=TELEGRAM_ID, first_name="Leo", user=user)


@pytest.fixture
def game_set(db, user):
    game_set = GameSet.objects.create(user=user, name="firma")
    Game.objects.create(user=user, game_set=game_set, numbers=list(range(1, 16)))
    return game_set


def _command_update(args: list[str]) -> tuple[MagicMock, MagicMock]:
    update = MagicMock()
    update.effective_user.id = TELEGRAM_ID
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = args
    return update, context


def _callback_update(data: str, telegram_id: int = TELEGRAM_ID) -> MagicMock:
    update = MagicMock()
    update.callback_query.data = data
    update.callback_query.from_user.id = telegram_id
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    return update


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestApagarHandler:
    async def test_without_name_lists_sets(self, tg_user, game_set) -> None:
        update, context = _command_update([])
        await apagar_handler(update, context)
        text = update.message.reply_text.call_args.args[0]
        assert "firma (1 jogo(s))" in text

    async def test_asks_confirmation_without_deleting(self, tg_user, game_set) -> None:
        update, context = _command_update(["FIRMA"])
        await apagar_handler(update, context)
        kwargs = update.message.reply_text.call_args.kwargs
        buttons = kwargs["reply_markup"].inline_keyboard[0]
        assert buttons[0].callback_data == f"{CALLBACK_PREFIX}{game_set.pk}"
        assert await GameSet.objects.filter(pk=game_set.pk).aexists()

    async def test_unknown_name(self, tg_user, game_set) -> None:
        update, context = _command_update(["nada"])
        await apagar_handler(update, context)
        assert "Não encontrei" in update.message.reply_text.call_args.args[0]

    async def test_confirm_deletes_set(self, tg_user, game_set) -> None:
        update = _callback_update(f"{CALLBACK_PREFIX}{game_set.pk}")
        await apagar_confirm(update, MagicMock())
        assert not await GameSet.objects.filter(pk=game_set.pk).aexists()
        assert "apagado (1 jogo(s))" in update.callback_query.edit_message_text.call_args.args[0]

    async def test_cancel_keeps_set(self, tg_user, game_set) -> None:
        update = _callback_update(f"{CALLBACK_PREFIX}cancel")
        await apagar_confirm(update, MagicMock())
        assert await GameSet.objects.filter(pk=game_set.pk).aexists()

    async def test_confirm_from_another_user_does_not_delete(self, tg_user, game_set) -> None:
        intruder = await User.objects.acreate(username="intruso")
        await TelegramUser.objects.acreate(telegram_id=999, first_name="X", user=intruder)
        update = _callback_update(f"{CALLBACK_PREFIX}{game_set.pk}", telegram_id=999)
        await apagar_confirm(update, MagicMock())
        assert await GameSet.objects.filter(pk=game_set.pk).aexists()
        assert "já não existe" in update.callback_query.edit_message_text.call_args.args[0]
