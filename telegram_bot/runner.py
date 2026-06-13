from django.conf import settings
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters

from telegram_bot.handlers import (
    error_handler,
    help_handler,
    latest_handler,
    mygames_handler,
    registrar_cancel,
    registrar_count,
    registrar_numbers,
    registrar_start,
    start_handler,
    suggest_cancel,
    suggest_count,
    suggest_size,
    suggest_start,
    sync_handler,
)
from telegram_bot.handlers.register_handler import ASK_COUNT as REG_ASK_COUNT
from telegram_bot.handlers.register_handler import ASK_NUMBERS as REG_ASK_NUMBERS
from telegram_bot.handlers.suggest_handler import ASK_COUNT as SUG_ASK_COUNT
from telegram_bot.handlers.suggest_handler import ASK_SIZE as SUG_ASK_SIZE


def create_application() -> Application:
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("latest", latest_handler))
    app.add_handler(CommandHandler("mygames", mygames_handler))
    app.add_handler(CommandHandler("atualizar", sync_handler))
    app.add_handler(CommandHandler("help", help_handler))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("suggest", suggest_start)],
        states={
            SUG_ASK_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, suggest_size)],
            SUG_ASK_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, suggest_count)],
        },
        fallbacks=[CommandHandler("cancelar", suggest_cancel)],
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("registrar", registrar_start)],
        states={
            REG_ASK_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_count)],
            REG_ASK_NUMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_numbers)],
        },
        fallbacks=[CommandHandler("cancelar", registrar_cancel)],
    ))

    app.add_error_handler(error_handler)
    return app


def run() -> None:
    # run_polling() gerencia o event loop internamente no PTB v21+
    create_application().run_polling()
