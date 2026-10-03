import pytest
from django.contrib.auth import get_user_model

from loterias.services.game_set_service import GameSetError, GameSetService

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="leo", password="pass")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="other", password="pass")


@pytest.mark.django_db
class TestGameSetService:
    def test_rejects_blank_name(self, user) -> None:
        with pytest.raises(GameSetError, match="apelido"):
            GameSetService().open(user, "   ")

    def test_rejects_long_name(self, user) -> None:
        with pytest.raises(GameSetError, match="40"):
            GameSetService().open(user, "a" * 41)

    def test_reuses_existing_name_ignoring_case(self, user) -> None:
        service = GameSetService()
        first = service.open(user, "Bolão da firma")
        second = service.open(user, "bolão da firma")
        assert second.pk == first.pk

    def test_same_name_for_another_user_is_a_different_set(self, user, other_user) -> None:
        service = GameSetService()
        first = service.open(user, "firma")
        second = service.open(other_user, "firma")
        assert second.pk != first.pk
