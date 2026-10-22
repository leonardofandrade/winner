import pytest
from django.contrib.auth import get_user_model

from loterias.services.game_set_service import (
    GameSetError,
    GameSetNotFoundError,
    GameSetService,
)

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


@pytest.mark.django_db
class TestGameSetRename:
    def test_renames_own_set(self, user) -> None:
        service = GameSetService()
        game_set = service.open(user, "firma")
        renamed = service.rename(user, game_set.pk, "  Bolão   da firma ")
        assert renamed.name == "Bolão da firma"

    def test_allows_changing_only_case(self, user) -> None:
        service = GameSetService()
        game_set = service.open(user, "firma")
        assert service.rename(user, game_set.pk, "Firma").name == "Firma"

    def test_rejects_name_of_another_own_set(self, user) -> None:
        service = GameSetService()
        service.open(user, "família")
        game_set = service.open(user, "firma")
        with pytest.raises(GameSetError, match="família"):
            service.rename(user, game_set.pk, "Família")

    def test_rejects_set_of_another_user(self, user, other_user) -> None:
        game_set = GameSetService().open(other_user, "firma")
        with pytest.raises(GameSetNotFoundError):
            GameSetService().rename(user, game_set.pk, "minha")
