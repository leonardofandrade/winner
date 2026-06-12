from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.repositories import TelegramUserRepository
from telegram_bot.services import RegisterGameService
from telegram_bot.services.register_game_service import RegisterGameError

_repo = TelegramUserRepository()
_service = RegisterGameService()

_USAGE = (
    "Envie os números do seu jogo junto com o comando:\n"
    "`/registrar 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15`\n\n"
    "Entre 15 e 20 dezenas, valores de 1 a 25, sem repetição."
)


async def register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(_USAGE, parse_mode="Markdown")
        return

    tg_user = await sync_to_async(_repo.get_by_telegram_id)(update.effective_user.id)
    if tg_user is None:
        await update.message.reply_text("Use /start primeiro para se registrar.")
        return

    text = " ".join(context.args)
    try:
        game = await sync_to_async(_service.execute)(tg_user, text)
    except RegisterGameError as exc:
        await update.message.reply_text(f"Erro: {exc}")
        return

    nums = "  ".join(f"{n:02d}" for n in game.numbers)
    await update.message.reply_text(
        f"Jogo #{game.pk} registrado com sucesso!\n\n`{nums}`",
        parse_mode="Markdown",
    )
