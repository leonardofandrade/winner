import logging
from decimal import Decimal

from asgiref.sync import sync_to_async
from django.conf import settings
from telegram import Bot

from loterias.models import Contest, Game, GameResult
from loterias.repositories import GameRepository
from loterias.services import ResultCalculationService
from telegram_bot.models import TelegramUser

logger = logging.getLogger(__name__)

_HIT_EMOJI = {15: "🏆", 14: "🥇", 13: "🎉", 12: "👍", 11: "✅"}
_MIN_PRIZE_HITS = 11


def _fmt_brl(value: Decimal) -> str:
    """Formata Decimal como R$ 1.234,50."""
    formatted = f"{value:,.2f}"
    return "R$ " + formatted.replace(",", "X").replace(".", ",").replace("X", ".")


class NotifyResultsService:
    """Calcula resultados de um concurso e envia notificações via Telegram."""

    def __init__(self) -> None:
        self._game_repo = GameRepository()
        self._calc = ResultCalculationService()

    async def notify_contest(self, contest: Contest) -> None:
        """Notifica todos os usuários vinculados sobre os resultados do concurso."""
        tg_users = await sync_to_async(list)(
            TelegramUser.objects.select_related("user").filter(user__isnull=False)
        )
        if not tg_users:
            return

        async with Bot(token=settings.TELEGRAM_BOT_TOKEN) as bot:
            for tg_user in tg_users:
                await self._notify_user(bot, tg_user, contest)

    async def _notify_user(self, bot: Bot, tg_user: TelegramUser, contest: Contest) -> None:
        games = await sync_to_async(list)(self._game_repo.get_by_user(tg_user.user))
        if not games:
            return

        pairs: list[tuple[Game, GameResult]] = []
        for game in games:
            result = await sync_to_async(self._calc.calculate)(game, contest)
            pairs.append((game, result))

        text = self._build_message(contest, pairs)
        await bot.send_message(chat_id=tg_user.telegram_id, text=text, parse_mode="Markdown")
        logger.info("Contest #%s — notified telegram_id=%s", contest.number, tg_user.telegram_id)

    def _build_message(self, contest: Contest, pairs: list[tuple[Game, GameResult]]) -> str:
        date_str = contest.draw_date.strftime("%d/%m/%Y")
        sorteio = "  ".join(f"{n:02d}" for n in contest.winning_numbers)
        lines = [
            f"🎰 *Concurso #{contest.number}* — {date_str}",
            f"`{sorteio}`\n",
        ]

        total_prize = Decimal("0")
        for game, result in pairs:
            emoji = _HIT_EMOJI.get(result.hits, "")
            if result.hits >= _MIN_PRIZE_HITS:
                lines.append(
                    f"{emoji} Jogo #{game.pk}: *{result.hits} acertos* — {_fmt_brl(result.prize)}"
                )
                total_prize += result.prize
            else:
                lines.append(f"Jogo #{game.pk}: {result.hits} acertos")

        if total_prize > 0:
            lines.append(f"\n💰 *Total: {_fmt_brl(total_prize)}*")

        return "\n".join(lines)
