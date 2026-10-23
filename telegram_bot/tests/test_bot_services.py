from datetime import date
from unittest.mock import patch

import pytest
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
        assert game.game_set_id is None

    def test_registers_game_inside_named_set(self, telegram_user) -> None:
        from loterias.services import GameSetService

        game_set = GameSetService().open(telegram_user.user, "bolão da firma")
        text = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"
        game = RegisterGameService().execute(telegram_user, text, game_set=game_set)
        assert game.game_set_id == game_set.pk
        again = GameSetService().open(telegram_user.user, "Bolão da firma")
        assert again.pk == game_set.pk

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


GAME_15 = "01 02 03 04 05 06 07 08 09 10 11 12 13 14 15"
GAME_16 = "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16"


class TestRegisterManyGames:
    def test_parse_detects_size_per_line(self) -> None:
        games = RegisterGameService().parse_games(f"{GAME_15}\n\n{GAME_16}\n")
        assert [len(g) for g in games] == [15, 16]

    def test_parse_accepts_mixed_separators_and_sorts(self) -> None:
        games = RegisterGameService().parse_games("15-14-13-12-11-10-9-8-7-6-5-4-3-2-1")
        assert games == [list(range(1, 16))]

    def test_parse_reports_every_bad_line(self) -> None:
        text = f"{GAME_15}\n1 2 3\n{GAME_15}\n1 1 3 4 5 6 7 8 9 10 11 12 13 14 15"
        with pytest.raises(RegisterGameError) as exc:
            RegisterGameService().parse_games(text)
        message = str(exc.value)
        assert "Linha 2:" in message and "(veio com 3)" in message
        assert "Linha 4:" in message and "repetir" in message
        assert "Linha 1" not in message

    def test_parse_rejects_empty_text(self) -> None:
        with pytest.raises(RegisterGameError, match="um jogo por linha"):
            RegisterGameService().parse_games("  \n ")

    def test_execute_many_saves_all_in_set(self, telegram_user) -> None:
        from loterias.services import GameSetService

        game_set = GameSetService().open(telegram_user.user, "firma")
        games = RegisterGameService().parse_games(f"{GAME_15}\n{GAME_16}")
        assert RegisterGameService().execute_many(telegram_user, games, game_set=game_set) == 2
        assert Game.objects.filter(game_set=game_set).count() == 2

    def test_execute_many_requires_link(self, telegram_user_no_link) -> None:
        with pytest.raises(RegisterGameError, match="vincular"):
            RegisterGameService().execute_many(telegram_user_no_link, [list(range(1, 16))])


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
