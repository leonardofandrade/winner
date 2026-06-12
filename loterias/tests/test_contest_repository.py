import pytest
from datetime import date

from loterias.models import Contest
from loterias.repositories import ContestRepository


@pytest.fixture
def repository() -> ContestRepository:
    return ContestRepository()


@pytest.fixture
def sample_parsed() -> dict:
    return {
        "number": 3095,
        "draw_date": date(2026, 6, 11),
        "winning_numbers": [3, 5, 7, 8, 10, 11, 12, 14, 16, 17, 19, 20, 21, 23, 25],
        "prize_pool": 48_500_000.00,
        "accumulated": False,
    }


@pytest.mark.django_db
class TestContestRepository:
    def test_update_or_create_creates_new(self, repository, sample_parsed) -> None:
        contest, created = repository.update_or_create(sample_parsed)
        assert created is True
        assert contest.number == 3095
        assert Contest.objects.count() == 1

    def test_update_or_create_updates_existing(self, repository, sample_parsed) -> None:
        repository.update_or_create(sample_parsed)
        updated = {**sample_parsed, "accumulated": True}
        contest, created = repository.update_or_create(updated)
        assert created is False
        assert contest.accumulated is True
        assert Contest.objects.count() == 1

    def test_get_by_number_found(self, repository, sample_parsed) -> None:
        repository.update_or_create(sample_parsed)
        contest = repository.get_by_number(3095)
        assert contest is not None
        assert contest.number == 3095

    def test_get_by_number_not_found(self, repository) -> None:
        assert repository.get_by_number(9999) is None

    def test_get_latest_number_empty_db(self, repository) -> None:
        assert repository.get_latest_number() is None

    def test_get_latest_number_returns_highest(self, repository, sample_parsed) -> None:
        repository.update_or_create(sample_parsed)
        repository.update_or_create({**sample_parsed, "number": 3096})
        assert repository.get_latest_number() == 3096
