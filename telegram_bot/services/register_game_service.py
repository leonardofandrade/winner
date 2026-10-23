import re

from core.exceptions import WinnerException
from loterias.models import Game, GameSet
from loterias.repositories import GameRepository
from telegram_bot.models import TelegramUser


class RegisterGameError(WinnerException):
    """Erro ao registrar jogo via Telegram."""


class RegisterGameService:
    """Parseia números de uma mensagem de texto e registra jogos para o usuário."""

    _MIN_NUMBERS = 15
    _MAX_NUMBERS = 20
    _MIN_VALUE = 1
    _MAX_VALUE = 25

    def __init__(self) -> None:
        self._games = GameRepository()

    def execute(self, telegram_user: TelegramUser, text: str, game_set: GameSet | None = None) -> Game:
        if telegram_user.user is None:
            raise RegisterGameError("Você precisa vincular sua conta Winner primeiro. Use /vincular.")

        numbers = self._parse_numbers(text)
        self._validate(numbers)
        return self._games.create(telegram_user.user, numbers, game_set=game_set)

    def parse_games(self, text: str) -> list[list[int]]:
        """
        Lê um jogo por linha, com a quantidade de dezenas detectada em cada uma.
        Valida todas as linhas antes e lista todos os erros de uma vez.
        """
        games: list[list[int]] = []
        errors: list[str] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            # Qualquer coisa que não seja dígito separa as dezenas: espaço, vírgula, hífen...
            numbers = [int(token) for token in re.findall(r"\d+", line)]
            if not numbers:
                continue
            try:
                self._validate(numbers)
            except RegisterGameError as exc:
                errors.append(
                    f"Linha {line_number}: {str(exc).rstrip('.')} (veio com {len(numbers)})."
                )
                continue
            games.append(sorted(numbers))
        if errors:
            raise RegisterGameError("\n".join(errors))
        if not games:
            raise RegisterGameError("Nenhum jogo encontrado. Envie um jogo por linha.")
        return games

    def execute_many(
        self, telegram_user: TelegramUser, games: list[list[int]], game_set: GameSet | None = None
    ) -> int:
        """Salva jogos já validados por parse_games. Retorna quantos foram salvos."""
        if telegram_user.user is None:
            raise RegisterGameError("Você precisa vincular sua conta Winner primeiro. Use /vincular.")
        return self._games.create_many(telegram_user.user, games, game_set=game_set)

    def _parse_numbers(self, text: str) -> list[int]:
        try:
            return [int(t) for t in text.split() if t.isdigit()]
        except ValueError as exc:
            raise RegisterGameError("Envie apenas números separados por espaço.") from exc

    def _validate(self, numbers: list[int]) -> None:
        if len(numbers) < self._MIN_NUMBERS or len(numbers) > self._MAX_NUMBERS:
            raise RegisterGameError(
                f"Um jogo precisa ter entre {self._MIN_NUMBERS} e {self._MAX_NUMBERS} dezenas."
            )
        if any(n < self._MIN_VALUE or n > self._MAX_VALUE for n in numbers):
            raise RegisterGameError("Todas as dezenas devem estar entre 1 e 25.")
        if len(set(numbers)) != len(numbers):
            raise RegisterGameError("As dezenas não podem se repetir.")
