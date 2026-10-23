"""Constantes compartilhadas do bot."""

from datetime import time
from zoneinfo import ZoneInfo

# Preços oficiais da Lotofácil por quantidade de dezenas (base: 15 = R$ 3,50)
# Fórmula: C(N,15) * R$ 3,50
GAME_PRICES: dict[int, str] = {
    15: "R$ 3,50",
    16: "R$ 56,00",
    17: "R$ 476,00",
    18: "R$ 2.856,00",
    19: "R$ 13.566,00",
    20: "R$ 54.264,00",
}

VALID_GAME_SIZES: set[int] = set(GAME_PRICES.keys())

# Horário do relatório diário de prêmios (horário de Brasília)
DAILY_REPORT_TIME = time(3, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))

# Comandos públicos do bot: fonte única para o menu "/" do Telegram, o /start e o /help
BOT_COMMANDS: list[tuple[str, str]] = [
    ("start", "Registrar e ver o menu"),
    ("latest", "Resultado do último concurso"),
    ("suggest", "Sugestões de jogos por frequência"),
    ("mygames", "Seus jogos e resultados"),
    ("registrar", "Cadastrar um conjunto de jogos"),
    ("apagar", "Apagar um conjunto de jogos pelo apelido"),
    ("ganhei", "Simular o aviso de 15 acertos"),
    ("help", "Ajuda"),
]


def commands_text() -> str:
    """Lista de comandos, uma linha por comando, para mensagens do bot."""
    return "\n".join(f"/{name} — {description}" for name, description in BOT_COMMANDS)
