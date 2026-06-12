import logging
from decimal import Decimal

from loterias.models import Contest, Game, GameResult
from loterias.repositories import ContestRepository, GameRepository, GameResultRepository

logger = logging.getLogger(__name__)

# Prêmios fixos por faixa (independem do concurso)
# 14 e 15 acertos são variáveis — dependem do rateio do concurso e ficam como 0
_FIXED_PRIZES: dict[int, Decimal] = {
    11: Decimal("6.00"),
    12: Decimal("12.00"),
    13: Decimal("25.00"),
}


class ResultCalculationService:
    """Calcula e persiste os acertos de jogos contra concursos."""

    def __init__(self) -> None:
        self._game_repo = GameRepository()
        self._contest_repo = ContestRepository()
        self._result_repo = GameResultRepository()

    def calculate(self, game: Game, contest: Contest) -> GameResult:
        """Calcula os acertos de um jogo em um concurso e salva o resultado."""
        hits = len(set(game.numbers) & set(contest.winning_numbers))
        prize = _FIXED_PRIZES.get(hits, Decimal("0"))
        result = self._result_repo.save(game, contest, hits, prize)
        logger.debug("Game #%s vs Contest #%s: %s hits, prize R$%s", game.pk, contest.number, hits, prize)
        return result

    def calculate_all_for_contest(self, contest: Contest) -> list[GameResult]:
        """Calcula todos os jogos cadastrados contra um único concurso."""
        results = [self.calculate(game, contest) for game in self._game_repo.get_all()]
        logger.info("Contest #%s: %s game results calculated.", contest.number, len(results))
        return results

    def calculate_all_for_game(self, game: Game) -> list[GameResult]:
        """Calcula um jogo contra todos os concursos cadastrados."""
        results = [
            self.calculate(game, contest)
            for contest in Contest.objects.order_by("number")
        ]
        logger.info("Game #%s: %s contest results calculated.", game.pk, len(results))
        return results
