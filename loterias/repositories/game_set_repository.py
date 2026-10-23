from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Count

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

    def list_with_game_count(self, user: AbstractBaseUser) -> list[GameSet]:
        """Conjuntos do usuário em ordem alfabética, com games_count anotado."""
        return list(
            GameSet.objects.filter(user=user).annotate(games_count=Count("games")).order_by("name")
        )

    def count_games(self, game_set: GameSet) -> int:
        return game_set.games.count()

    def delete(self, game_set: GameSet) -> None:
        # Jogos e resultados do conjunto são apagados em cascata
        game_set.delete()
