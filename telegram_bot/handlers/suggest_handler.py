from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from telegram_bot.services import BotSuggestionsService

_service = BotSuggestionsService()

# Estados da conversa
ASK_SIZE, ASK_COUNT = range(2)

_VALID_SIZES = set(range(15, 21))
_MAX_GAMES = 10

# Preço base: 1 jogo de 15 dezenas = R$ 3,50
# Demais calculados por C(25,N)/C(25,15) * 3.50
_PRICES = {
    15: "R$ 3,50",
    16: "R$ 56,00",
    17: "R$ 476,00",
    18: "R$ 2.856,00",
    19: "R$ 13.566,00",
    20: "R$ 54.264,00",
}


async def suggest_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sizes = "  ".join(str(s) for s in range(15, 21))
    await update.message.reply_text(
        "Quantas dezenas por jogo?\n"
        f"`{sizes}`",
        parse_mode="Markdown",
    )
    return ASK_SIZE


async def suggest_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    try:
        size = int(text)
    except ValueError:
        await update.message.reply_text("Envie apenas o número (ex: `15`). Tente de novo:", parse_mode="Markdown")
        return ASK_SIZE

    if size not in _VALID_SIZES:
        await update.message.reply_text("Escolha entre *15 e 20* dezenas. Tente de novo:", parse_mode="Markdown")
        return ASK_SIZE

    context.user_data["suggest_size"] = size
    price = _PRICES[size]
    await update.message.reply_text(
        f"Jogo de *{size} dezenas* — {price} cada.\n\n"
        f"Quantos jogos você quer? (1 a {_MAX_GAMES})",
        parse_mode="Markdown",
    )
    return ASK_COUNT


async def suggest_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    size = context.user_data.get("suggest_size", 15)

    try:
        count = int(text)
    except ValueError:
        await update.message.reply_text("Envie apenas o número (ex: `3`). Tente de novo:", parse_mode="Markdown")
        return ASK_COUNT

    if count < 1 or count > _MAX_GAMES:
        await update.message.reply_text(f"Escolha entre *1 e {_MAX_GAMES}* jogos. Tente de novo:", parse_mode="Markdown")
        return ASK_COUNT

    suggestions = await sync_to_async(_service.get_suggestions)(count=count, size=size)
    price = _PRICES[size]
    lines = "\n".join(f"  `{s}`" for s in suggestions)
    total_label = f"  Total: {count}x {price}" if count > 1 else f"  {price}"

    await update.message.reply_text(
        f"*Sugestões — {size} dezenas* (análise de frequência):\n\n"
        + lines
        + f"\n\n{total_label}",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def suggest_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Sugestão cancelada.")
    return ConversationHandler.END
