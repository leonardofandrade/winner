from django.contrib.auth.models import AbstractBaseUser

from core.exceptions import WinnerException
from loterias.models import GameSet
from loterias.repositories import GameSetRepository


class GameSetError(WinnerException):
    """Apelido de conjunto inválido."""


class GameSetNotFoundError(GameSetError):
    """Conjunto inexistente ou de outro usuário."""


class GameSetService:
    """Abre, renomeia e apaga conjuntos de jogos pelo apelido."""

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

    def rename(self, user: AbstractBaseUser, set_id: int, name: str) -> GameSet:
        game_set = self._repo.get_for_user_by_id(user, set_id)
        if game_set is None:
            raise GameSetNotFoundError("Conjunto não encontrado.")
        cleaned = self.clean_name(name)
        # Mudar só maiúsculas/minúsculas do próprio conjunto é permitido
        existing = self._repo.get_for_user_by_name(user, cleaned)
        if existing is not None and existing.pk != game_set.pk:
            raise GameSetError(f"Você já tem um conjunto chamado {existing.name}.")
        return self._repo.rename(game_set, cleaned)

    def find(self, user: AbstractBaseUser, name: str) -> GameSet | None:
        """Busca um conjunto do usuário pelo apelido, ignorando maiúsculas e espaços extras."""
        return self._repo.get_for_user_by_name(user, self.clean_name(name))

    def list_for_user(self, user: AbstractBaseUser) -> list[GameSet]:
        return self._repo.list_with_game_count(user)

    def count_games(self, game_set: GameSet) -> int:
        return self._repo.count_games(game_set)

    def delete(self, user: AbstractBaseUser, set_id: int) -> tuple[str, int]:
        """Apaga o conjunto e seus jogos. Retorna (apelido, quantidade de jogos apagados)."""
        game_set = self._repo.get_for_user_by_id(user, set_id)
        if game_set is None:
            raise GameSetNotFoundError("Conjunto não encontrado.")
        name, games = game_set.name, self._repo.count_games(game_set)
        self._repo.delete(game_set)
        return name, games
