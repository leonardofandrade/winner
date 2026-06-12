from core.exceptions import WinnerException
from loterias.models import Game
from telegram_bot.models import TelegramUser


class RegisterGameError(WinnerException):
    """Erro ao registrar jogo via Telegram."""


class RegisterGameService:
    """Parseia números de uma mensagem de texto e registra o jogo para o usuário."""

    _MIN_NUMBERS = 15
    _MAX_NUMBERS = 20
    _MIN_VALUE = 1
    _MAX_VALUE = 25

    def execute(self, telegram_user: TelegramUser, text: str) -> Game:
        if telegram_user.user is None:
            raise RegisterGameError("Você precisa vincular sua conta Winner primeiro. Use /vincular.")

        numbers = self._parse_numbers(text)
        self._validate(numbers)
        return Game.objects.create(user=telegram_user.user, numbers=numbers)

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
