# Resposta real da API da Caixa — concurso 3095 (usado nos testes)
CONTEST_3095_RAW = {
    "numero": 3095,
    "dataApuracao": "11/06/2026",
    "listaDezenas": ["03", "05", "07", "08", "10", "11", "12", "14", "16", "17", "19", "20", "21", "23", "25"],
    "acumulado": False,
    "valorArrecadado": 48_500_000.00,
    "listaRateioPremio": [
        {"faixa": 1, "numeroDeGanhadores": 2, "valorPremio": 1_250_000.00},
        {"faixa": 2, "numeroDeGanhadores": 120, "valorPremio": 1_500.00},
    ],
}

# Resposta com concurso acumulado
CONTEST_ACCUMULATED_RAW = {
    "numero": 3096,
    "dataApuracao": "13/06/2026",
    "listaDezenas": ["01", "02", "04", "06", "09", "10", "13", "15", "16", "18", "20", "21", "22", "24", "25"],
    "acumulado": True,
    "valorArrecadado": 52_000_000.00,
    "listaRateioPremio": [],
}
