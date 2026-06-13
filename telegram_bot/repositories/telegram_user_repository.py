from telegram_bot.models import TelegramUser


class TelegramUserRepository:
    """Encapsula todo acesso ORM ao model TelegramUser."""

    def get_or_create(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str,
    ) -> tuple[TelegramUser, bool]:
        return TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={"username": username, "first_name": first_name},
        )

    def get_by_telegram_id(self, telegram_id: int) -> TelegramUser | None:
        return TelegramUser.objects.select_related("user").filter(telegram_id=telegram_id).first()
