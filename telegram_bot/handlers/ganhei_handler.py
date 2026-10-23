from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.repositories import TelegramUserRepository
from telegram_bot.services import SimulateWinService

_repo = TelegramUserRepository()
_service = SimulateWinService()


async def ganhei_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = await sync_to_async(_repo.get_by_telegram_id)(update.effective_user.id)
    text = await sync_to_async(_service.execute)(tg_user)
    if text is None:
        await update.message.reply_text("Nenhum concurso importado ainda. Tente mais tarde.")
        return
    await update.message.reply_text(text, parse_mode="Markdown")
