from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.services import GetLatestContestService

_service = GetLatestContestService()


async def latest_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    contest = await sync_to_async(_service.execute)()
    if contest is None:
        await update.message.reply_text("Nenhum concurso importado ainda. Tente mais tarde.")
        return

    numbers_str = "  ".join(f"{n:02d}" for n in sorted(contest.winning_numbers))
    await update.message.reply_text(
        f"*Concurso #{contest.number}* — {contest.draw_date.strftime('%d/%m/%Y')}\n\n"
        f"`{numbers_str}`\n\n"
        f"Acumulado: {'Sim' if contest.accumulated else 'Não'}",
        parse_mode="Markdown",
    )
