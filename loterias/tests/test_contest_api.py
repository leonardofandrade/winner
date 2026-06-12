import pytest
from datetime import date
from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APIClient

from loterias.models import Contest


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def contest(db):
    return Contest.objects.create(
        number=3095,
        draw_date=date(2026, 6, 11),
        winning_numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        prize_pool=Decimal("48500000.00"),
        accumulated=False,
    )


@pytest.mark.django_db
class TestContestListView:
    def test_returns_200(self, client, contest) -> None:
        response = client.get(reverse("contest-list"))
        assert response.status_code == 200

    def test_returns_contest_in_list(self, client, contest) -> None:
        response = client.get(reverse("contest-list"))
        assert response.data["count"] == 1
        assert response.data["results"][0]["number"] == 3095

    def test_ordered_by_number_desc(self, client, db) -> None:
        Contest.objects.create(number=1, draw_date=date(2003, 9, 29), winning_numbers=list(range(1, 16)))
        Contest.objects.create(number=2, draw_date=date(2003, 10, 6), winning_numbers=list(range(1, 16)))
        response = client.get(reverse("contest-list"))
        numbers = [r["number"] for r in response.data["results"]]
        assert numbers == sorted(numbers, reverse=True)

    def test_no_auth_required(self, client, contest) -> None:
        response = client.get(reverse("contest-list"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestContestDetailView:
    def test_returns_200(self, client, contest) -> None:
        response = client.get(reverse("contest-detail", kwargs={"number": 3095}))
        assert response.status_code == 200

    def test_returns_correct_fields(self, client, contest) -> None:
        response = client.get(reverse("contest-detail", kwargs={"number": 3095}))
        assert response.data["number"] == 3095
        assert response.data["winning_numbers"] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

    def test_returns_404_for_unknown_contest(self, client, db) -> None:
        response = client.get(reverse("contest-detail", kwargs={"number": 9999}))
        assert response.status_code == 404
