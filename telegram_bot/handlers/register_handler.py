from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from loterias.models import Game
from loterias.services.game_set_service import GameSetError, GameSetService
from telegram_bot.constants import GAME_PRICES, VALID_GAME_SIZES
from telegram_bot.models import TelegramUser
from telegram_bot.repositories import TelegramUserRepository
from telegram_bot.services import RegisterGameService
from telegram_bot.services.register_game_service import RegisterGameError

_repo = TelegramUserRepository()
_games = RegisterGameService()
_sets = GameSetService()

# Estados da conversa
ASK_NAME, ASK_COUNT, ASK_NUMBERS = range(3)


def _md(value: str) -> str:
    return "".join(f"\\{ch}" if ch in "\\_*`[" else ch for ch in value)


def _register(telegram_user: TelegramUser, text: str, name: str) -> Game:
    game_set = _sets.open(telegram_user.user, name)
    return _games.execute(telegram_user, text, game_set=game_set)


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

    context.user_data["register_saved"] = 0
    await update.message.reply_text(
        "Qual o apelido deste conjunto de jogos?\n"
        "Exemplo: `bolão da firma`",
        parse_mode="Markdown",
    )
    return ASK_NAME


async def registrar_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        name = _sets.clean_name(update.message.text)
    except GameSetError as exc:
        await update.message.reply_text(f"{exc}\n\nTente de novo:")
        return ASK_NAME

    context.user_data["register_name"] = name
    await update.message.reply_text(
        f"Conjunto *{_md(name)}*.\n\n"
        "Quantas dezenas no primeiro jogo?\n"
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

    if count not in VALID_GAME_SIZES:
        await update.message.reply_text("Escolha entre *15 e 20* dezenas. Tente de novo:", parse_mode="Markdown")
        return ASK_COUNT

    context.user_data["register_count"] = count
    price = GAME_PRICES[count]
    await update.message.reply_text(
        f"Jogo de *{count} dezenas* — {price}.\n\n"
        f"Envie as {count} dezenas separadas por espaço:\n"
        f"Valores de 1 a 25, sem repetição.\n\n"
        f"Use /cancelar para desistir.",
        parse_mode="Markdown",
    )
    return ASK_NUMBERS


async def registrar_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    expected = context.user_data.get("register_count", 15)
    name = context.user_data.get("register_name", "")
    text = update.message.text.strip()

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
        game = await sync_to_async(_register)(tg_user, text, name)
    except (RegisterGameError, GameSetError) as exc:
        await update.message.reply_text(f"Erro: {exc}\n\nTente novamente:")
        return ASK_NUMBERS

    saved = context.user_data.get("register_saved", 0) + 1
    context.user_data["register_saved"] = saved
    nums = "  ".join(f"{n:02d}" for n in game.numbers)
    await update.message.reply_text(
        f"Jogo #{game.pk} salvo em *{_md(name)}*.\n\n"
        f"`{nums}`\n\n"
        "Outro jogo neste conjunto? Digite de *15 a 20* dezenas, ou /pronto para encerrar.",
        parse_mode="Markdown",
    )
    return ASK_COUNT


async def registrar_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    saved = context.user_data.get("register_saved", 0)
    name = context.user_data.get("register_name", "")
    if saved:
        await update.message.reply_text(
            f"Conjunto *{_md(name)}* salvo com {saved} jogo(s).",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text("Nenhum jogo foi salvo.")
    return ConversationHandler.END


async def registrar_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    saved = context.user_data.get("register_saved", 0)
    if saved:
        name = context.user_data.get("register_name", "")
        await update.message.reply_text(
            f"Registro interrompido. {saved} jogo(s) já estão em *{_md(name)}*.",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text("Registro cancelado.")
    return ConversationHandler.END
