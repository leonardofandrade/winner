from django.contrib.auth.models import AbstractBaseUser

from core.exceptions import WinnerException
from loterias.models import GameSet
from loterias.repositories import GameSetRepository


class GameSetError(WinnerException):
    """Apelido de conjunto inválido."""


class GameSetService:
    """Abre um conjunto de jogos pelo apelido, reutilizando o que já existe."""

    MAX_NAME_LENGTH = 40

    def __init__(self) -> None:
        self._repo = GameSetRepository()

    def clean_name(self, name: str) -> str:
        cleaned = " ".join(name.split())
        if not cleaned:
            raise GameSetError("Informe um apelido.")
        if len(cleaned) > self.MAX_NAME_LENGTH:
            raise GameSetError(f"O apelido pode ter no máximo {self.MAX_NAME_LENGTH} caracteres.")
        return cleaned

    def open(self, user: AbstractBaseUser, name: str) -> GameSet:
        cleaned = self.clean_name(name)
        existing = self._repo.get_for_user_by_name(user, cleaned)
        if existing is not None:
            return existing
        return self._repo.create(user, cleaned)
