"""Constantes compartilhadas do bot."""

from datetime import time, timedelta
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
BOT_TIMEZONE = ZoneInfo("America/Sao_Paulo")
DAILY_REPORT_TIME = time(0, 0, tzinfo=BOT_TIMEZONE)

# A Caixa às vezes leva horas para publicar o sorteio na API. Se à meia-noite o
# concurso de ontem ainda não saiu, o relatório tenta de novo neste intervalo
# (16 tentativas de 30 min = até as 8h).
DAILY_REPORT_RETRY_INTERVAL = timedelta(minutes=30)
DAILY_REPORT_MAX_RETRIES = 16

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
