import pytest
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from loterias.models import Contest, Game, GameResult

User = get_user_model()

NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


@pytest.fixture
def user(db):
    return User.objects.create_user(username="leo", password="pass123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="other", password="pass123")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def contest(db):
    return Contest.objects.create(
        number=3095,
        draw_date=date(2026, 6, 11),
        winning_numbers=NUMBERS,
        accumulated=False,
    )


@pytest.mark.django_db
class TestGameListCreateView:
    def test_list_requires_auth(self) -> None:
        response = APIClient().get(reverse("game-list"))
        assert response.status_code == 403

    def test_list_returns_only_own_games(self, auth_client, user, other_user) -> None:
        Game.objects.create(user=user, numbers=NUMBERS)
        Game.objects.create(user=other_user, numbers=NUMBERS)
        response = auth_client.get(reverse("game-list"))
        assert response.data["count"] == 1

    def test_create_game(self, auth_client) -> None:
        response = auth_client.post(reverse("game-list"), {"numbers": NUMBERS}, format="json")
        assert response.status_code == 201
        assert Game.objects.count() == 1

    def test_create_sets_authenticated_user(self, auth_client, user) -> None:
        auth_client.post(reverse("game-list"), {"numbers": NUMBERS}, format="json")
        game = Game.objects.first()
        assert game.user == user

    def test_create_requires_auth(self) -> None:
        response = APIClient().post(reverse("game-list"), {"numbers": NUMBERS}, format="json")
        assert response.status_code == 403


@pytest.mark.django_db
class TestGameDetailView:
    def test_retrieve_own_game(self, auth_client, user) -> None:
        game = Game.objects.create(user=user, numbers=NUMBERS)
        response = auth_client.get(reverse("game-detail", kwargs={"pk": game.pk}))
        assert response.status_code == 200

    def test_cannot_retrieve_other_users_game(self, auth_client, other_user) -> None:
        game = Game.objects.create(user=other_user, numbers=NUMBERS)
        response = auth_client.get(reverse("game-detail", kwargs={"pk": game.pk}))
        assert response.status_code == 404

    def test_delete_own_game(self, auth_client, user) -> None:
        game = Game.objects.create(user=user, numbers=NUMBERS)
        response = auth_client.delete(reverse("game-detail", kwargs={"pk": game.pk}))
        assert response.status_code == 204
        assert Game.objects.count() == 0

    def test_cannot_delete_other_users_game(self, auth_client, other_user) -> None:
        game = Game.objects.create(user=other_user, numbers=NUMBERS)
        response = auth_client.delete(reverse("game-detail", kwargs={"pk": game.pk}))
        assert response.status_code == 404
        assert Game.objects.count() == 1


@pytest.mark.django_db
class TestGameResultsView:
    def test_returns_results_for_own_game(self, auth_client, user, contest) -> None:
        game = Game.objects.create(user=user, numbers=NUMBERS)
        GameResult.objects.create(game=game, contest=contest, hits=15, prize=Decimal("0"))
        response = auth_client.get(reverse("game-results", kwargs={"pk": game.pk}))
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_returns_404_for_other_users_game(self, auth_client, other_user, contest) -> None:
        game = Game.objects.create(user=other_user, numbers=NUMBERS)
        response = auth_client.get(reverse("game-results", kwargs={"pk": game.pk}))
        assert response.status_code == 404
