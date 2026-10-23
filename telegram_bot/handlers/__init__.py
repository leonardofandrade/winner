from .apagar_handler import apagar_confirm, apagar_handler
from .error_handler import error_handler
from .ganhei_handler import ganhei_handler
from .help_handler import help_handler
from .latest_handler import latest_handler
from .mygames_handler import mygames_handler
from .register_handler import (
    registrar_cancel,
    registrar_done,
    registrar_games,
    registrar_name,
    registrar_start,
)
from .start_handler import start_handler
from .suggest_handler import suggest_cancel, suggest_count, suggest_size, suggest_start
from .sync_handler import sync_handler

__all__ = [
    "apagar_confirm",
    "apagar_handler",
    "error_handler",
    "ganhei_handler",
    "start_handler",
    "latest_handler",
    "suggest_start",
    "suggest_size",
    "suggest_count",
    "suggest_cancel",
    "mygames_handler",
    "registrar_start",
    "registrar_name",
    "registrar_games",
    "registrar_done",
    "registrar_cancel",
    "sync_handler",
    "help_handler",
]
