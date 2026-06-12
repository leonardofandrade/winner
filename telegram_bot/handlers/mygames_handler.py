from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.repositories import TelegramUserRepository
from telegram_bot.services import GetUserGamesService

_repo = TelegramUserRepository()
_service = GetUserGamesService()


async def mygames_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = await sync_to_async(_repo.get_by_telegram_id)(update.effective_user.id)

    if tg_user is None:
        await update.message.reply_text("Use /start primeiro para se registrar.")
        return

    games = await sync_to_async(_service.execute)(tg_user)

    if games is None:
        await update.message.reply_text(
            "Sua conta Telegram não está vinculada a uma conta Winner.\n"
            "Entre em contato com o administrador para vincular."
        )
        return

    games_list = await sync_to_async(list)(games[:10])
    if not games_list:
        await update.message.reply_text("Você ainda não tem jogos cadastrados.")
        return

    lines = []
    for game in games_list:
        nums = "  ".join(f"{n:02d}" for n in game.numbers)
        lines.append(f"Jogo #{game.pk}: `{nums}`")

    await update.message.reply_text(
        "*Seus últimos jogos:*\n\n" + "\n".join(lines),
        parse_mode="Markdown",
    )
