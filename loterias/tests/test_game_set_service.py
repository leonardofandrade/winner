import pytest
from django.contrib.auth import get_user_model

from loterias.models import Game, GameSet
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


@pytest.mark.django_db
class TestGameSetDelete:
    def test_find_ignores_case_and_extra_spaces(self, user) -> None:
        game_set = GameSetService().open(user, "Bolão da firma")
        assert GameSetService().find(user, "  bolão   DA firma ").pk == game_set.pk

    def test_find_returns_none_for_unknown_name(self, user) -> None:
        assert GameSetService().find(user, "nada") is None

    def test_delete_removes_set_and_games(self, user) -> None:
        game_set = GameSetService().open(user, "firma")
        Game.objects.create(user=user, game_set=game_set, numbers=list(range(1, 16)))
        Game.objects.create(user=user, numbers=list(range(1, 16)))

        assert GameSetService().delete(user, game_set.pk) == ("firma", 1)
        assert not GameSet.objects.filter(pk=game_set.pk).exists()
        # Jogo sem conjunto continua
        assert Game.objects.count() == 1

    def test_delete_rejects_set_of_another_user(self, user, other_user) -> None:
        game_set = GameSetService().open(other_user, "firma")
        with pytest.raises(GameSetNotFoundError):
            GameSetService().delete(user, game_set.pk)
        assert GameSet.objects.filter(pk=game_set.pk).exists()

    def test_list_for_user_counts_games(self, user, other_user) -> None:
        firma = GameSetService().open(user, "firma")
        GameSetService().open(user, "amigos")
        GameSetService().open(other_user, "outro")
        Game.objects.create(user=user, game_set=firma, numbers=list(range(1, 16)))

        sets = GameSetService().list_for_user(user)
        assert [(s.name, s.games_count) for s in sets] == [("amigos", 0), ("firma", 1)]
