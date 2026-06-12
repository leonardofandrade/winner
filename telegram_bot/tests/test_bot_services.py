import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model

from loterias.models import Contest, Game
from telegram_bot.models import TelegramUser
from telegram_bot.services import (
    BotSuggestionsService,
    GetLatestContestService,
    GetUserGamesService,
    RegisterGameService,
)
from telegram_bot.services.register_game_service import RegisterGameError

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="leo", password="pass")


@pytest.fixture
def telegram_user(db, user):
    return TelegramUser.objects.create(telegram_id=123456, username="leo", first_name="Leo", user=user)


@pytest.fixture
def telegram_user_no_link(db):
    return TelegramUser.objects.create(telegram_id=999999, username="anon", first_name="Anon")


@pytest.fixture
def contest(db):
    return Contest.objects.create(
        number=3095, draw_date=date(2026, 6, 11),
        winning_numbers=list(range(1, 16)), accumulated=False,
    )


@pytest.mark.django_db
class TestGetLatestContestService:
    def test_returns_none_when_empty(self) -> None:
        assert GetLatestContestService().execute() is None

    def test_returns_latest_contest(self, contest) -> None:
        result = GetLatestContestService().execute()
        assert result.number == 3095


@pytest.mark.django_db
class TestGetUserGamesService:
    def test_returns_none_when_not_linked(self, telegram_user_no_link) -> None:
        result = GetUserGamesService().execute(telegram_user_no_link)
        assert result is None

    def test_returns_queryset_when_linked(self, telegram_user, user) -> None:
        Game.objects.create(user=user, numbers=list(range(1, 16)))
        result = GetUserGamesService().execute(telegram_user)
        assert result is not None
        assert result.count() == 1


@pytest.mark.django_db
class TestRegisterGameService:
    def test_registers_game_from_text(self, telegram_user) -> None:
        text = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"
        game = RegisterGameService().execute(telegram_user, text)
        assert game.pk is not None
        assert game.numbers == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

    def test_raises_when_not_linked(self, telegram_user_no_link) -> None:
        with pytest.raises(RegisterGameError, match="vincular"):
            RegisterGameService().execute(telegram_user_no_link, "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15")

    def test_raises_when_too_few_numbers(self, telegram_user) -> None:
        with pytest.raises(RegisterGameError):
            RegisterGameService().execute(telegram_user, "1 2 3")

    def test_raises_when_numbers_out_of_range(self, telegram_user) -> None:
        with pytest.raises(RegisterGameError):
            RegisterGameService().execute(telegram_user, "0 2 3 4 5 6 7 8 9 10 11 12 13 14 15")

    def test_raises_when_duplicate_numbers(self, telegram_user) -> None:
        with pytest.raises(RegisterGameError):
            RegisterGameService().execute(telegram_user, "1 1 3 4 5 6 7 8 9 10 11 12 13 14 15")


class TestBotSuggestionsService:
    def test_returns_formatted_strings(self) -> None:
        service = BotSuggestionsService()
        with patch.object(service._generator, "generate", return_value=[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]]):
            result = service.get_suggestions(count=1)
        assert len(result) == 1
        assert "01" in result[0]
        assert "15" in result[0]

    def test_returns_correct_count(self) -> None:
        service = BotSuggestionsService()
        games = [list(range(1, 16))] * 3
        with patch.object(service._generator, "generate", return_value=games):
            result = service.get_suggestions(count=3)
        assert len(result) == 3
