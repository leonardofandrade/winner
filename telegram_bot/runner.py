from django.conf import settings
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters

from telegram_bot.handlers import (
    help_handler,
    latest_handler,
    mygames_handler,
    registrar_cancel,
    registrar_count,
    registrar_numbers,
    registrar_start,
    start_handler,
    suggest_handler,
)
from telegram_bot.handlers.register_handler import ASK_COUNT, ASK_NUMBERS


def create_application() -> Application:
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("latest", latest_handler))
    app.add_handler(CommandHandler("suggest", suggest_handler))
    app.add_handler(CommandHandler("mygames", mygames_handler))
    app.add_handler(CommandHandler("help", help_handler))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("registrar", registrar_start)],
        states={
            ASK_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_count)],
            ASK_NUMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_numbers)],
        },
        fallbacks=[CommandHandler("cancelar", registrar_cancel)],
    ))

    return app


def run() -> None:
    # run_polling() gerencia o event loop internamente no PTB v21+
    create_application().run_polling()
