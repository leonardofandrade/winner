from django.contrib.auth.models import AbstractBaseUser

from loterias.models import GameSet


class GameSetRepository:
    """Encapsula todo acesso ORM ao model GameSet."""

    def get_for_user_by_name(self, user: AbstractBaseUser, name: str) -> GameSet | None:
        return GameSet.objects.filter(user=user, name__iexact=name).first()

    def create(self, user: AbstractBaseUser, name: str) -> GameSet:
        return GameSet.objects.create(user=user, name=name)

    def get_for_user_by_id(self, user: AbstractBaseUser, set_id: int) -> GameSet | None:
        return GameSet.objects.filter(user=user, pk=set_id).first()

    def rename(self, game_set: GameSet, name: str) -> GameSet:
        game_set.name = name
        game_set.save(update_fields=["name", "updated_at"])
        return game_set
