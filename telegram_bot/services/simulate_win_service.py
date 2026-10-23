from decimal import Decimal

from loterias.models import Contest, Game, GameResult
from loterias.repositories import ContestRepository, GameRepository
from telegram_bot.models import TelegramUser
from telegram_bot.services.notify_results_service import NotifyResultsService

_JACKPOT_HITS = 15
# Concursos recentes consultados em busca de um rateio real de 15 acertos
_JACKPOT_LOOKBACK = 50
# Usado só se nenhum concurso recente teve ganhador de 15 acertos
_FALLBACK_PRIZE = Decimal("1500000.00")


class SimulateWinService:
    """Monta a mensagem de resultado como se o usuário tivesse acertado os 15 pontos."""

    def __init__(self) -> None:
        self._contest_repo = ContestRepository()
        self._game_repo = GameRepository()
        self._notify = NotifyResultsService()

    def execute(self, telegram_user: TelegramUser | None) -> str | None:
        """Retorna a mensagem simulada, ou None se ainda não houver concursos importados."""
        contest = self._contest_repo.get_latest()
        if contest is None:
            return None
        game = self._simulated_game(telegram_user, contest)
        # Objetos em memória: nada é gravado no banco
        result = GameResult(game=game, contest=contest, hits=_JACKPOT_HITS, prize=self._jackpot_prize())
        message = self._notify.build_message(contest, [(game, result)])
        return f"🧪 *Simulação* — é assim que chega o aviso no dia em que você acertar os 15:\n\n{message}"

    def _simulated_game(self, telegram_user: TelegramUser | None, contest: Contest) -> Game:
        # Usa o jogo mais recente do usuário para o rótulo ficar igual ao real
        if telegram_user is not None and telegram_user.user is not None:
            real = self._game_repo.get_by_user(telegram_user.user).first()
            if real is not None:
                return Game(
                    pk=real.pk, user=real.user, game_set=real.game_set,
                    numbers=list(contest.winning_numbers),
                )
        return Game(pk=1, numbers=list(contest.winning_numbers))

    def _jackpot_prize(self) -> Decimal:
        for contest in self._contest_repo.get_recent(_JACKPOT_LOOKBACK):
            value = Decimal(str((contest.prize_tiers or {}).get(str(_JACKPOT_HITS), 0)))
            if value > 0:
                return value
        return _FALLBACK_PRIZE
