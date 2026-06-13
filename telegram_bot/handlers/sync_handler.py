from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.repositories import TelegramUserRepository

_repo = TelegramUserRepository()


async def sync_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = await sync_to_async(_repo.get_by_telegram_id)(update.effective_user.id)

    if tg_user is None or tg_user.user is None or not tg_user.user.is_staff:
        await update.message.reply_text("Comando restrito a administradores.")
        return

    await update.message.reply_text("Verificando concursos novos...")

    from loterias.services import ImportLotofacilService

    service = ImportLotofacilService()
    latest_number, imported = await service.sync()

    if imported == 0:
        await update.message.reply_text(f"Banco já atualizado. Último concurso: #{latest_number}.")
    else:
        await update.message.reply_text(
            f"{imported} concurso(s) importado(s). Último: #{latest_number}."
        )
