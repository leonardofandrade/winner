from django.test import override_settings
from telegram.ext import CommandHandler, ConversationHandler

from telegram_bot.constants import BOT_COMMANDS, commands_text
from telegram_bot.runner import create_application


def _handled_commands() -> set[str]:
    with override_settings(TELEGRAM_BOT_TOKEN="123:abc"):
        app = create_application()
    commands: set[str] = set()
    for handlers in app.handlers.values():
        for handler in handlers:
            entries = handler.entry_points if isinstance(handler, ConversationHandler) else [handler]
            for entry in entries:
                if isinstance(entry, CommandHandler):
                    commands |= set(entry.commands)
    return commands


class TestCommandMenu:
    def test_every_listed_command_has_a_handler(self) -> None:
        missing = {name for name, _ in BOT_COMMANDS} - _handled_commands()
        assert not missing

    def test_commands_text_lists_every_command(self) -> None:
        text = commands_text()
        assert all(f"/{name} — " in text for name, _ in BOT_COMMANDS)
