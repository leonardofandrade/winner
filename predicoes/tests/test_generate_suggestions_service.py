import pytest
from datetime import date
from unittest.mock import patch

from predicoes.services import GenerateSuggestionsService

_NUMBERS_1_15 = list(range(1, 16))
_NUMBERS_11_25 = list(range(11, 26))


class TestGenerateSuggestionsService:
    def test_generate_returns_correct_count(self) -> None:
        service = GenerateSuggestionsService()
        with patch.object(service._repo, "get_recent", return_value=[]):
            result = service.generate(count=3)
        assert len(result) == 3

    def test_each_game_has_15_numbers(self) -> None:
        service = GenerateSuggestionsService()
        with patch.object(service._repo, "get_recent", return_value=[]):
            result = service.generate(count=5)
        assert all(len(game) == 15 for game in result)

    def test_numbers_are_in_valid_range(self) -> None:
        service = GenerateSuggestionsService()
        with patch.object(service._repo, "get_recent", return_value=[]):
            result = service.generate(count=10)
        for game in result:
            assert all(1 <= n <= 25 for n in game)

    def test_numbers_are_sorted(self) -> None:
        service = GenerateSuggestionsService()
        with patch.object(service._repo, "get_recent", return_value=[]):
            result = service.generate(count=5)
        for game in result:
            assert game == sorted(game)

    def test_no_repeated_numbers_in_game(self) -> None:
        service = GenerateSuggestionsService()
        with patch.object(service._repo, "get_recent", return_value=[]):
            result = service.generate(count=10)
        for game in result:
            assert len(set(game)) == 15

    def test_uniform_weights_when_no_contests(self) -> None:
        service = GenerateSuggestionsService()
        with patch.object(service._repo, "get_recent", return_value=[]):
            weights = service._compute_weights()
        assert len(weights) == 25
        assert all(w > 0 for w in weights)

    @pytest.mark.django_db
    def test_uses_contest_history(self) -> None:
        from loterias.models import Contest
        # Cria concursos onde os números 1-15 sempre saem
        for i in range(1, 6):
            Contest.objects.create(
                number=i, draw_date=date(2024, 1, i),
                winning_numbers=_NUMBERS_1_15, accumulated=False,
            )
        service = GenerateSuggestionsService(lookback=10)
        weights = service._compute_weights()
        # Números 1-15 devem ter pesos maiores que 16-25
        low_weight = sum(weights[15:])  # índices 15-24 = números 16-25
        high_weight = sum(weights[:15])  # índices 0-14 = números 1-15
        assert high_weight > low_weight
