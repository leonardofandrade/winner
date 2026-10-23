from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from loterias.repositories import GameResultRepository
from telegram_bot.repositories import TelegramUserRepository
from telegram_bot.services import GetUserGamesService
from telegram_bot.utils import split_message

_repo = TelegramUserRepository()
_service = GetUserGamesService()
_results = GameResultRepository()

_RESULT_LIMIT = 5   # concursos recentes por jogo
_MIN_PRIZE_HITS = 11

_HIT_EMOJI = {15: "🏆", 14: "🥇", 13: "🎉", 12: "👍", 11: "✅"}


def _md(value: str) -> str:
    return "".join(f"\\{ch}" if ch in "\\_*`[" else ch for ch in value)


async def mygames_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = await sync_to_async(_repo.get_by_telegram_id)(update.effective_user.id)

    if tg_user is None:
        await update.message.reply_text("Use /start primeiro para se registrar.")
        return

    games_qs = await sync_to_async(_service.execute)(tg_user)
    if games_qs is None:
        await update.message.reply_text(
            "Sua conta Telegram não está vinculada a uma conta Winner.\n"
            "Entre em contato com o administrador para vincular."
        )
        return

    games = await sync_to_async(list)(games_qs)
    if not games:
        await update.message.reply_text("Você ainda não tem jogos cadastrados.\nUse /registrar para cadastrar.")
        return

    grouped: dict[str | None, list] = {}
    for game in games:
        label = game.game_set.name if game.game_set_id else None
        grouped.setdefault(label, []).append(game)

    lines = [f"*Seus jogos ({len(games)}):*\n"]
    for label, group in grouped.items():
        title = _md(label) if label else "Sem apelido"
        lines.append(f"*{title}* ({len(group)} jogo(s))")
        for game in group:
            nums = "  ".join(f"{n:02d}" for n in game.numbers)
            lines.append(f"*Jogo #{game.pk}* ({len(game.numbers)} dezenas)")
            lines.append(f"`{nums}`")

            results = await sync_to_async(list)(_results.get_for_game(game)[:_RESULT_LIMIT])

            if results:
                for r in results:
                    emoji = _HIT_EMOJI.get(r.hits, "")
                    if r.hits >= _MIN_PRIZE_HITS:
                        prize = f"R$ {r.prize:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        lines.append(f"  {emoji} #{r.contest.number}: *{r.hits} acertos* — {prize}")
                    else:
                        lines.append(f"  #{r.contest.number}: {r.hits} acertos")
            else:
                lines.append("  _Sem resultados calculados ainda_")

        lines.append("")

    # Com muitos jogos o texto passa do limite do Telegram: envia em partes
    for chunk in split_message("\n".join(lines)):
        await update.message.reply_text(chunk, parse_mode="Markdown")
