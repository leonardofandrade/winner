from datetime import date, datetime, time, timedelta

from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from loterias.models import Game, GameSet


class GameRepository:
    """Encapsula todo acesso ORM ao model Game."""

    def get_by_id(self, game_id: int) -> Game | None:
        return Game.objects.filter(pk=game_id).first()

    def get_by_user(self, user: AbstractBaseUser) -> QuerySet[Game]:
        return Game.objects.filter(user=user).select_related("game_set").order_by("-created_at")

    def get_by_user_until(self, user: AbstractBaseUser, draw_date: date) -> QuerySet[Game]:
        """Jogos do usuário cadastrados até o fim do dia do sorteio."""
        # Limite calculado em Python: __date no MySQL exige as tabelas de timezone carregadas
        limit = timezone.make_aware(datetime.combine(draw_date + timedelta(days=1), time.min))
        return self.get_by_user(user).filter(created_at__lt=limit)

    def create(self, user: AbstractBaseUser, numbers: list[int], game_set: GameSet | None = None) -> Game:
        return Game.objects.create(user=user, numbers=numbers, game_set=game_set)

    def create_many(
        self, user: AbstractBaseUser, games: list[list[int]], game_set: GameSet | None = None
    ) -> int:
        """Cria vários jogos de uma vez: ou todos são salvos, ou nenhum."""
        with transaction.atomic():
            for numbers in games:
                Game.objects.create(user=user, numbers=numbers, game_set=game_set)
        return len(games)

    def get_by_id_for_user(self, game_id: int, user: AbstractBaseUser) -> Game | None:
        return Game.objects.filter(pk=game_id, user=user).first()

    def get_all(self) -> QuerySet[Game]:
        return Game.objects.all()
