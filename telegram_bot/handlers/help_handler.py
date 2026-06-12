from telegram import Update
from telegram.ext import ContextTypes


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "*Winner Bot — Ajuda*\n\n"
        "/start — Registrar e ver menu\n"
        "/latest — Resultado do último concurso\n"
        "/suggest — Sugestões de jogos por frequência\n"
        "/mygames — Seus jogos cadastrados\n"
        "/registrar — Cadastrar um jogo\n"
        "/help — Esta mensagem\n\n"
        "*Cadastrar um jogo:*\n"
        "`/registrar 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15`\n"
        "Entre 15 e 20 dezenas, valores de 1 a 25, sem repetição.",
        parse_mode="Markdown",
    )
