from django.contrib.auth.models import AbstractBaseUser
from django.db.models import QuerySet

from loterias.models import Game, GameSet


class GameRepository:
    """Encapsula todo acesso ORM ao model Game."""

    def get_by_id(self, game_id: int) -> Game | None:
        return Game.objects.filter(pk=game_id).first()

    def get_by_user(self, user: AbstractBaseUser) -> QuerySet[Game]:
        return Game.objects.filter(user=user).select_related("game_set").order_by("-created_at")

    def create(self, user: AbstractBaseUser, numbers: list[int], game_set: GameSet | None = None) -> Game:
        return Game.objects.create(user=user, numbers=numbers, game_set=game_set)

    def get_by_id_for_user(self, game_id: int, user: AbstractBaseUser) -> Game | None:
        return Game.objects.filter(pk=game_id, user=user).first()

    def get_all(self) -> QuerySet[Game]:
        return Game.objects.all()
