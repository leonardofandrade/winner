from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.constants import commands_text


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "*Winner Bot — Ajuda*\n\n"
        f"{commands_text()}\n\n"
        "*Cadastrar jogos:*\n"
        "/registrar pede um apelido, as dezenas e os números.\n"
        "Depois de cada jogo, envie outro ou /pronto para encerrar.\n"
        "Entre 15 e 20 dezenas, valores de 1 a 25, sem repetição.\n\n"
        "*Apagar jogos:*\n"
        "`/apagar bolão da firma` pede confirmação antes de apagar o conjunto.",
        parse_mode="Markdown",
    )
