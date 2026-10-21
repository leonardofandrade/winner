from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Exibe queries SQL no terminal durante desenvolvimento
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        # O httpx loga a URL de cada request, e a URL da API do Telegram contém o token do bot
        "httpx": {"level": "WARNING"},
    },
}
