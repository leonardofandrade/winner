from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from loterias.models import Contest
from loterias.services import ImportLotofacilService
from loterias.tests.fixtures import CONTEST_3095_RAW


def _make_contest(number: int = 3095) -> Contest:
    return Contest(
        number=number,
        draw_date=date(2026, 6, 11),
        winning_numbers=[3, 5, 7, 8, 10, 11, 12, 14, 16, 17, 19, 20, 21, 23, 25],
        prize_pool=48_500_000.00,
        accumulated=False,
    )


@pytest.fixture
def service() -> ImportLotofacilService:
    return ImportLotofacilService()


@pytest.mark.asyncio
class TestImportLotofacilService:
    async def test_import_contest_calls_client_with_number(self, service) -> None:
        contest = _make_contest()

        def fake_sync_to_async(f):
            # Envolve a função síncrona num wrapper async para o teste
            async def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
            return wrapper

        with (
            patch.object(service._client, "fetch_contest", new=AsyncMock(return_value=CONTEST_3095_RAW)),
            patch.object(service._repository, "update_or_create", return_value=(contest, True)),
            patch("loterias.services.import_lotofacil_service.sync_to_async", side_effect=fake_sync_to_async),
        ):
            result = await service.import_contest(3095)
            service._client.fetch_contest.assert_awaited_once_with(3095)
            assert result is contest

    async def test_import_contest_without_number_calls_client_with_none(self, service) -> None:
        contest = _make_contest()

        def fake_sync_to_async(f):
            async def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
            return wrapper

        with (
            patch.object(service._client, "fetch_contest", new=AsyncMock(return_value=CONTEST_3095_RAW)),
            patch.object(service._repository, "update_or_create", return_value=(contest, True)),
            patch("loterias.services.import_lotofacil_service.sync_to_async", side_effect=fake_sync_to_async),
        ):
            await service.import_contest()
            service._client.fetch_contest.assert_awaited_once_with(None)

    async def test_import_range_returns_all_successful(self, service) -> None:
        contests = [_make_contest(n) for n in (3095, 3096)]
        results_iter = iter(contests)

        async def fake_import(number=None):
            return next(results_iter)

        with patch.object(service, "import_contest", side_effect=fake_import):
            result = await service.import_range(3095, 3096)
            assert len(result) == 2

    async def test_import_range_skips_failed_contest(self, service) -> None:
        contest = _make_contest(3096)
        call_count = 0

        async def fake_import(number=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("API error")
            return contest

        with patch.object(service, "import_contest", side_effect=fake_import):
            result = await service.import_range(3095, 3096)
            # Primeiro falhou, segundo passou
            assert len(result) == 1
            assert result[0] is contest
