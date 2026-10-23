from collections import Counter

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from loterias.services.game_set_service import GameSetError, GameSetService
from telegram_bot.constants import GAME_PRICES
from telegram_bot.models import TelegramUser
from telegram_bot.repositories import TelegramUserRepository
from telegram_bot.services import RegisterGameService
from telegram_bot.services.register_game_service import RegisterGameError

_repo = TelegramUserRepository()
_games = RegisterGameService()
_sets = GameSetService()

# Estados da conversa
ASK_NAME, ASK_GAMES = range(2)

_GAMES_PROMPT = (
    "Envie os jogos, *um por linha*. Pode mandar vários de uma vez.\n"
    "Cada linha com 15 a 20 dezenas, de 1 a 25, sem repetição.\n\n"
    "Exemplo:\n"
    "`01 02 03 04 05 06 07 08 09 10 11 12 13 14 15`\n"
    "`02 04 06 08 10 12 14 16 18 20 21 22 23 24 25`"
)


def _md(value: str) -> str:
    return "".join(f"\\{ch}" if ch in "\\_*`[" else ch for ch in value)


def _register_many(telegram_user: TelegramUser, games: list[list[int]], name: str) -> int:
    game_set = _sets.open(telegram_user.user, name)
    return _games.execute_many(telegram_user, games, game_set=game_set)


def _summary(games: list[list[int]]) -> str:
    """Resumo por quantidade de dezenas, ex.: '• 3 jogo(s) de 15 dezenas — R$ 3,50 cada'."""
    sizes = Counter(len(numbers) for numbers in games)
    return "\n".join(
        f"• {count} jogo(s) de {size} dezenas — {GAME_PRICES[size]} cada"
        for size, count in sorted(sizes.items())
    )


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
        "Exemplo: `bolão da firma`\n\n"
        "Se o apelido já existir, os jogos entram nesse conjunto.",
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
        f"Conjunto *{_md(name)}*.\n\n{_GAMES_PROMPT}\n\nUse /cancelar para desistir.",
        parse_mode="Markdown",
    )
    return ASK_GAMES


async def registrar_games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = context.user_data.get("register_name", "")
    try:
        games = _games.parse_games(update.message.text)
    except RegisterGameError as exc:
        await update.message.reply_text(
            f"{exc}\n\nNenhum jogo foi salvo. Corrija e envie a lista de novo."
        )
        return ASK_GAMES

    tg_user = await sync_to_async(_repo.get_by_telegram_id)(update.effective_user.id)
    try:
        saved_now = await sync_to_async(_register_many)(tg_user, games, name)
    except (RegisterGameError, GameSetError) as exc:
        await update.message.reply_text(f"Erro: {exc}\n\nTente novamente:")
        return ASK_GAMES

    saved = context.user_data.get("register_saved", 0) + saved_now
    context.user_data["register_saved"] = saved
    await update.message.reply_text(
        f"{saved_now} jogo(s) salvo(s) em *{_md(name)}*:\n{_summary(games)}\n\n"
        "Envie mais jogos para este conjunto, ou /pronto para encerrar.",
        parse_mode="Markdown",
    )
    return ASK_GAMES


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
