from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.repositories import TelegramUserRepository

_repo = TelegramUserRepository()


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    tg_user, created = await sync_to_async(_repo.get_or_create)(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name or "",
    )
    greeting = "Bem-vindo" if created else "Olá de novo"
    await update.message.reply_text(
        f"{greeting}, {user.first_name}! 🍀\n\n"
        "Comandos disponíveis:\n"
        "/latest — último concurso\n"
        "/suggest — sugestão de jogo\n"
        "/registrar — cadastrar um jogo\n"
        "/mygames — seus jogos e resultados\n"
        "/atualizar — importar novos concursos (admin)\n"
        "/help — ajuda"
    )
