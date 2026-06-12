from django.db.models import QuerySet

from loterias.models import Game
from loterias.repositories import GameRepository
from telegram_bot.models import TelegramUser


class GetUserGamesService:
    """Retorna os jogos do usuário Winner vinculado ao TelegramUser."""

    def __init__(self) -> None:
        self._repo = GameRepository()

    def execute(self, telegram_user: TelegramUser) -> QuerySet[Game] | None:
        """Retorna QuerySet de jogos, ou None se não houver conta Winner vinculada."""
        if telegram_user.user is None:
            return None
        return self._repo.get_by_user(telegram_user.user)
