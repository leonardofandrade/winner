from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.services import BotSuggestionsService

_service = BotSuggestionsService()


async def suggest_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    suggestions = await sync_to_async(_service.get_suggestions)(count=3)
    lines = "\n".join(f"  `{s}`" for s in suggestions)
    await update.message.reply_text(
        "*Sugestões de jogos* (análise de frequência):\n\n" + lines,
        parse_mode="Markdown",
    )
