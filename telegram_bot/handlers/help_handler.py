from telegram import Update
from telegram.ext import ContextTypes


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "*Winner Bot — Ajuda*\n\n"
        "/start — Registrar e ver menu\n"
        "/latest — Resultado do último concurso\n"
        "/suggest — Sugestões de jogos por frequência\n"
        "/mygames — Seus jogos cadastrados\n"
        "/registrar — Cadastrar um conjunto de jogos\n"
        "/help — Esta mensagem\n\n"
        "*Cadastrar jogos:*\n"
        "/registrar pede um apelido, as dezenas e os números.\n"
        "Depois de cada jogo, envie outro ou /pronto para encerrar.\n"
        "Entre 15 e 20 dezenas, valores de 1 a 25, sem repetição.",
        parse_mode="Markdown",
    )
