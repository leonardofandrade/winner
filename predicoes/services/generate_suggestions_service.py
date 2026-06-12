import random
from collections import Counter

from loterias.repositories import ContestRepository

_ALL_NUMBERS = list(range(1, 26))
_GAME_SIZE = 15
_DEFAULT_LOOKBACK = 100


class GenerateSuggestionsService:
    """
    Fase 7 (mock) — heurística de frequência.

    Conta quantas vezes cada dezena (1-25) saiu nos últimos N concursos e
    amostra 15 números com probabilidade proporcional à frequência.
    Números mais frequentes têm maior chance de aparecer na sugestão.
    """

    def __init__(self, lookback: int = _DEFAULT_LOOKBACK) -> None:
        self._lookback = lookback
        self._repo = ContestRepository()

    def generate(self, count: int = 1) -> list[list[int]]:
        """Gera `count` jogos sugeridos. Retorna lista de listas de 15 inteiros."""
        weights = self._compute_weights()
        return [self._sample_game(weights) for _ in range(count)]

    def _compute_weights(self) -> list[float]:
        """Calcula pesos normalizados para cada número 1-25 com base em frequência."""
        contests = self._repo.get_recent(self._lookback)
        if not contests:
            # Sem histórico → distribuição uniforme
            return [1.0] * 25

        counter: Counter = Counter()
        for contest in contests:
            counter.update(contest.winning_numbers)

        # Peso mínimo de 0.1 para que números nunca sorteados ainda tenham chance
        total = sum(counter.values())
        return [max(counter.get(n, 0) / total, 0.1 / 25) for n in _ALL_NUMBERS]

    def _sample_game(self, weights: list[float]) -> list[int]:
        """Amostra 15 números sem reposição usando os pesos calculados."""
        remaining = list(range(25))  # índices de _ALL_NUMBERS
        remaining_weights = list(weights)
        chosen: list[int] = []

        for _ in range(_GAME_SIZE):
            idx = random.choices(range(len(remaining)), weights=remaining_weights, k=1)[0]
            chosen.append(_ALL_NUMBERS[remaining.pop(idx)])
            remaining_weights.pop(idx)

        return sorted(chosen)
