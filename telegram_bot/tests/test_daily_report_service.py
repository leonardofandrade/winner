from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_bot.constants import DAILY_REPORT_MAX_RETRIES
from telegram_bot.jobs import daily_report_job
from telegram_bot.services import DailyReportService


@pytest.mark.asyncio
class TestDailyReportService:
    async def test_syncs_then_notifies(self) -> None:
        service = DailyReportService()
        bot = AsyncMock()
        with (
            patch.object(service._import, "sync", new=AsyncMock(return_value=(3709, 1))) as sync,
            patch.object(service._notify, "notify_pending", new=AsyncMock(return_value=2)) as notify,
        ):
            sent = await service.run(bot)
        sync.assert_awaited_once()
        notify.assert_awaited_once_with(bot)
        assert sent == 2

    async def test_notifies_even_if_sync_fails(self) -> None:
        service = DailyReportService()
        with (
            patch.object(service._import, "sync", new=AsyncMock(side_effect=RuntimeError("caixa down"))),
            patch.object(service._notify, "notify_pending", new=AsyncMock(return_value=1)) as notify,
        ):
            sent = await service.run(AsyncMock())
        notify.assert_awaited_once()
        assert sent == 1


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestHasYesterdaysDraw:
    async def _contest(self, draw_date) -> None:
        from loterias.models import Contest

        await Contest.objects.acreate(
            number=3833, draw_date=draw_date, winning_numbers=list(range(1, 16)), accumulated=False
        )

    async def test_true_when_yesterdays_draw_is_saved(self) -> None:
        await self._contest(date(2026, 11, 19))
        assert await DailyReportService().has_yesterdays_draw(today=date(2026, 11, 20))

    async def test_false_when_caixa_has_not_published_yet(self) -> None:
        await self._contest(date(2026, 11, 18))
        assert not await DailyReportService().has_yesterdays_draw(today=date(2026, 11, 20))

    async def test_false_on_empty_db(self) -> None:
        assert not await DailyReportService().has_yesterdays_draw(today=date(2026, 11, 20))


def _context(attempt: int | None) -> MagicMock:
    context = MagicMock()
    context.bot = AsyncMock()
    context.job.data = attempt
    return context


@pytest.mark.asyncio
class TestDailyReportJobRetry:
    async def _run(self, context: MagicMock, published: bool) -> None:
        with (
            patch("telegram_bot.jobs.daily_report_job.close_old_connections"),
            patch.object(DailyReportService, "run", new=AsyncMock(return_value=0)),
            patch.object(
                DailyReportService, "has_yesterdays_draw", new=AsyncMock(return_value=published)
            ),
        ):
            await daily_report_job(context)

    async def test_schedules_retry_when_draw_is_missing(self) -> None:
        context = _context(None)
        await self._run(context, published=False)
        context.job_queue.run_once.assert_called_once()
        assert context.job_queue.run_once.call_args.kwargs["data"] == 1

    async def test_no_retry_once_draw_is_published(self) -> None:
        context = _context(3)
        await self._run(context, published=True)
        context.job_queue.run_once.assert_not_called()

    async def test_gives_up_after_max_retries(self) -> None:
        context = _context(DAILY_REPORT_MAX_RETRIES)
        await self._run(context, published=False)
        context.job_queue.run_once.assert_not_called()
