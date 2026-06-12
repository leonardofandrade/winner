"""Constantes compartilhadas do bot."""

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
