from django.conf import settings
from telegram.ext import Application, CommandHandler

from telegram_bot.handlers import (
    help_handler,
    latest_handler,
    mygames_handler,
    register_handler,
    start_handler,
    suggest_handler,
)


def create_application() -> Application:
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("latest", latest_handler))
    app.add_handler(CommandHandler("suggest", suggest_handler))
    app.add_handler(CommandHandler("mygames", mygames_handler))
    app.add_handler(CommandHandler("registrar", register_handler))
    app.add_handler(CommandHandler("help", help_handler))
    return app


def run() -> None:
    # run_polling() gerencia o event loop internamente no PTB v21+
    create_application().run_polling()
