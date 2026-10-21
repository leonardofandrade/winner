from unittest.mock import AsyncMock, patch

import pytest

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
