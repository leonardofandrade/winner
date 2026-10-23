import logging
from decimal import Decimal

from asgiref.sync import sync_to_async
from telegram import Bot

from loterias.models import Contest, Game, GameResult
from loterias.repositories import ContestRepository, GameRepository
from loterias.services import ResultCalculationService
from telegram_bot.models import TelegramUser
from telegram_bot.repositories import TelegramUserRepository
from telegram_bot.utils import split_message

logger = logging.getLogger(__name__)

_HIT_EMOJI = {15: "🏆", 14: "🥇", 13: "🎉", 12: "👍", 11: "✅"}
_MIN_PRIZE_HITS = 11
# Após muitos dias sem rodar, envia só os concursos mais recentes para não inundar o chat
_MAX_CATCH_UP = 7


def _fmt_brl(value: Decimal) -> str:
    """Formata Decimal como R$ 1.234,50."""
    formatted = f"{value:,.2f}"
    return "R$ " + formatted.replace(",", "X").replace(".", ",").replace("X", ".")


class NotifyResultsService:
    """Calcula resultados dos concursos pendentes e envia notificações via Telegram."""

    def __init__(self) -> None:
        self._game_repo = GameRepository()
        self._contest_repo = ContestRepository()
        self._tg_repo = TelegramUserRepository()
        self._calc = ResultCalculationService()

    async def notify_pending(self, bot: Bot) -> int:
        """Envia a cada usuário vinculado os concursos ainda não notificados. Retorna o total enviado."""
        tg_users = await sync_to_async(self._tg_repo.get_linked)()
        sent = 0
        for tg_user in tg_users:
            try:
                sent += await self._notify_user(bot, tg_user)
            except Exception:
                # Não marca como notificado: o próximo envio tenta de novo
                logger.exception("Failed to notify telegram_id=%s.", tg_user.telegram_id)
        return sent

    async def _notify_user(self, bot: Bot, tg_user: TelegramUser) -> int:
        contests = await sync_to_async(self._pending_contests)(tg_user)
        sent = 0
        for contest in contests:
            if await self._notify_contest(bot, tg_user, contest):
                sent += 1
            await sync_to_async(self._tg_repo.set_last_notified)(tg_user, contest.number)
        return sent

    def _pending_contests(self, tg_user: TelegramUser) -> list[Contest]:
        # Primeiro envio do usuário: só o concurso mais recente
        if tg_user.last_notified_contest is None:
            latest = self._contest_repo.get_latest()
            return [latest] if latest else []
        return self._contest_repo.get_after(tg_user.last_notified_contest, _MAX_CATCH_UP)

    async def _notify_contest(self, bot: Bot, tg_user: TelegramUser, contest: Contest) -> bool:
        """Envia o resultado de um concurso. Retorna False se o usuário não tinha jogos nele."""
        games = await sync_to_async(list)(
            self._game_repo.get_by_user_until(tg_user.user, contest.draw_date)
        )
        if not games:
            return False

        pairs: list[tuple[Game, GameResult]] = []
        for game in games:
            result = await sync_to_async(self._calc.calculate)(game, contest)
            pairs.append((game, result))

        for chunk in split_message(self.build_message(contest, pairs)):
            await bot.send_message(chat_id=tg_user.telegram_id, text=chunk, parse_mode="Markdown")
        logger.info("Contest #%s — notified telegram_id=%s", contest.number, tg_user.telegram_id)
        return True

    def build_message(self, contest: Contest, pairs: list[tuple[Game, GameResult]]) -> str:
        date_str = contest.draw_date.strftime("%d/%m/%Y")
        sorteio = "  ".join(f"{n:02d}" for n in contest.winning_numbers)
        lines = [
            f"🎰 *Concurso #{contest.number}* — {date_str}",
            f"`{sorteio}`\n",
        ]

        total_prize = Decimal("0")
        for game, result in pairs:
            emoji = _HIT_EMOJI.get(result.hits, "")
            label = f"Jogo #{game.pk}"
            if game.game_set_id:
                safe_name = "".join(
                    f"\\{ch}" if ch in "\\_*`[" else ch for ch in game.game_set.name
                )
                label += f" ({safe_name})"
            if result.hits >= _MIN_PRIZE_HITS:
                lines.append(
                    f"{emoji} {label}: *{result.hits} acertos* — {_fmt_brl(result.prize)}"
                )
                total_prize += result.prize
            else:
                lines.append(f"{label}: {result.hits} acertos")

        if total_prize > 0:
            lines.append(f"\n💰 *Total: {_fmt_brl(total_prize)}*")

        return "\n".join(lines)
