from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.repositories import TelegramUserRepository
from telegram_bot.services import DailyReportService

_repo = TelegramUserRepository()


async def sync_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    tg_user = await sync_to_async(_repo.get_by_telegram_id)(update.effective_user.id)

    if tg_user is None or tg_user.user is None or not tg_user.user.is_staff:
        await message.reply_text("Comando restrito a administradores.")
        return

    await message.reply_text("Verificando concursos novos...")

    # Mesmo fluxo do relatório diário: importa e já envia os resultados pendentes
    sent = await DailyReportService().run(context.bot)

    if sent == 0:
        await message.reply_text("Nenhum resultado novo para enviar.")
    else:
        await message.reply_text(f"{sent} resultado(s) de concurso enviado(s).")
