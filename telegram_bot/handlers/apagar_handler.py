from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from loterias.models import GameSet
from loterias.services.game_set_service import GameSetError, GameSetNotFoundError, GameSetService
from telegram_bot.models import TelegramUser
from telegram_bot.repositories import TelegramUserRepository

_repo = TelegramUserRepository()
_sets = GameSetService()

# Prefixo do callback_data dos botões de confirmação
CALLBACK_PREFIX = "apagar:"
_CANCEL = "cancel"

_NOT_LINKED = (
    "Sua conta Telegram não está vinculada a uma conta Winner.\n"
    "Entre em contato com o administrador para vincular."
)


def _md(value: str) -> str:
    return "".join(f"\\{ch}" if ch in "\\_*`[" else ch for ch in value)


def _set_list(game_sets: list[GameSet]) -> str:
    if not game_sets:
        return "Você não tem conjuntos de jogos salvos."
    lines = [f"• {_md(s.name)} ({s.games_count} jogo(s))" for s in game_sets]
    return "Seus conjuntos:\n" + "\n".join(lines)


async def _linked_user(telegram_id: int) -> TelegramUser | None:
    tg_user = await sync_to_async(_repo.get_by_telegram_id)(telegram_id)
    if tg_user is None or tg_user.user is None:
        return None
    return tg_user


async def apagar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = await _linked_user(update.effective_user.id)
    if tg_user is None:
        await update.message.reply_text(_NOT_LINKED)
        return

    name = " ".join(context.args)
    if not name:
        game_sets = await sync_to_async(_sets.list_for_user)(tg_user.user)
        await update.message.reply_text(
            f"Use `/apagar <apelido>`.\n\n{_set_list(game_sets)}", parse_mode="Markdown"
        )
        return

    try:
        game_set = await sync_to_async(_sets.find)(tg_user.user, name)
    except GameSetError as exc:
        await update.message.reply_text(str(exc))
        return
    if game_set is None:
        game_sets = await sync_to_async(_sets.list_for_user)(tg_user.user)
        await update.message.reply_text(
            f"Não encontrei o conjunto *{_md(name)}*.\n\n{_set_list(game_sets)}", parse_mode="Markdown"
        )
        return

    games = await sync_to_async(_sets.count_games)(game_set)
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Sim, apagar", callback_data=f"{CALLBACK_PREFIX}{game_set.pk}"),
        InlineKeyboardButton("Cancelar", callback_data=f"{CALLBACK_PREFIX}{_CANCEL}"),
    ]])
    await update.message.reply_text(
        f"Apagar o conjunto *{_md(game_set.name)}* com {games} jogo(s)?\n"
        "Os resultados calculados desses jogos também serão apagados.",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def apagar_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    choice = query.data.removeprefix(CALLBACK_PREFIX)
    if choice == _CANCEL:
        await query.edit_message_text("Nada foi apagado.")
        return

    # Confere o dono de novo: o callback_data vem do cliente
    tg_user = await _linked_user(query.from_user.id)
    if tg_user is None:
        await query.edit_message_text(_NOT_LINKED)
        return

    try:
        name, games = await sync_to_async(_sets.delete)(tg_user.user, int(choice))
    except (GameSetNotFoundError, ValueError):
        await query.edit_message_text("Esse conjunto já não existe.")
        return
    await query.edit_message_text(
        f"Conjunto *{_md(name)}* apagado ({games} jogo(s)).", parse_mode="Markdown"
    )
