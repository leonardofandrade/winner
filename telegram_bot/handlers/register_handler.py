from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from telegram_bot.repositories import TelegramUserRepository
from telegram_bot.services import RegisterGameService
from telegram_bot.services.register_game_service import RegisterGameError

_repo = TelegramUserRepository()
_service = RegisterGameService()

# Estados da conversa
ASK_COUNT, ASK_NUMBERS = range(2)

_VALID_COUNTS = set(range(15, 21))  # 15..20


async def registrar_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tg_user = await sync_to_async(_repo.get_by_telegram_id)(update.effective_user.id)

    if tg_user is None:
        await update.message.reply_text("Use /start primeiro para se registrar.")
        return ConversationHandler.END

    if tg_user.user is None:
        await update.message.reply_text(
            "Sua conta Telegram não está vinculada a uma conta Winner.\n"
            "Entre em contato com o administrador para vincular."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Quantas dezenas você quer jogar?\n"
        "Digite um número de *15 a 20*:",
        parse_mode="Markdown",
    )
    return ASK_COUNT


async def registrar_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    try:
        count = int(text)
    except ValueError:
        await update.message.reply_text("Envie apenas o número (ex: `15`). Tente de novo:", parse_mode="Markdown")
        return ASK_COUNT

    if count not in _VALID_COUNTS:
        await update.message.reply_text("Escolha entre *15 e 20* dezenas. Tente de novo:", parse_mode="Markdown")
        return ASK_COUNT

    context.user_data["register_count"] = count
    await update.message.reply_text(
        f"Ótimo! Agora envie as *{count} dezenas* separadas por espaço:\n"
        f"Valores de 1 a 25, sem repetição.\n\n"
        f"Use /cancelar para desistir.",
        parse_mode="Markdown",
    )
    return ASK_NUMBERS


async def registrar_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    expected = context.user_data.get("register_count", 15)
    text = update.message.text.strip()

    # Valida quantidade antes de chamar o service
    tokens = [t for t in text.split() if t.isdigit()]
    if len(tokens) != expected:
        await update.message.reply_text(
            f"Você enviou {len(tokens)} dezena(s), mas escolheu jogar com {expected}.\n"
            f"Envie exatamente *{expected} dezenas*:",
            parse_mode="Markdown",
        )
        return ASK_NUMBERS

    tg_user = await sync_to_async(_repo.get_by_telegram_id)(update.effective_user.id)
    try:
        game = await sync_to_async(_service.execute)(tg_user, text)
    except RegisterGameError as exc:
        await update.message.reply_text(f"Erro: {exc}\n\nTente novamente:")
        return ASK_NUMBERS

    nums = "  ".join(f"{n:02d}" for n in game.numbers)
    await update.message.reply_text(
        f"Jogo #{game.pk} registrado com sucesso!\n\n`{nums}`",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def registrar_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Registro cancelado.")
    return ConversationHandler.END
