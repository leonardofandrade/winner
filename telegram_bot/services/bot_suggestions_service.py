from predicoes.services import GenerateSuggestionsService


class BotSuggestionsService:
    """Delega para GenerateSuggestionsService e formata a resposta para o bot."""

    def __init__(self) -> None:
        self._generator = GenerateSuggestionsService()

    def get_suggestions(self, count: int = 1, size: int = 15) -> list[str]:
        """Retorna lista de strings formatadas para envio no Telegram."""
        games = self._generator.generate(count=count, size=size)
        return [self._format(game) for game in games]

    def _format(self, numbers: list[int]) -> str:
        return "  ".join(f"{n:02d}" for n in numbers)
