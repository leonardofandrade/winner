from django.db.models import QuerySet

from loterias.models import Game


class GameRepository:
    """Encapsula todo acesso ORM ao model Game."""

    def get_by_id(self, game_id: int) -> Game | None:
        return Game.objects.filter(pk=game_id).first()

    def get_all(self) -> QuerySet[Game]:
        return Game.objects.all()
