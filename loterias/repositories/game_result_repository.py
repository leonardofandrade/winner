from decimal import Decimal

from django.db.models import QuerySet

from loterias.models import Contest, Game, GameResult


class GameResultRepository:
    """Encapsula todo acesso ORM ao model GameResult."""

    def save(self, game: Game, contest: Contest, hits: int, prize: Decimal) -> GameResult:
        """Cria ou atualiza o resultado de um jogo para um concurso."""
        result, _ = GameResult.objects.update_or_create(
            game=game,
            contest=contest,
            defaults={"hits": hits, "prize": prize},
        )
        return result

    def get_for_game(self, game: Game) -> QuerySet[GameResult]:
        return GameResult.objects.filter(game=game).select_related("contest").order_by("-contest__number")

    def get_for_contest(self, contest: Contest) -> QuerySet[GameResult]:
        return GameResult.objects.filter(contest=contest).select_related("game").order_by("-hits")
