# Limite de caracteres por mensagem imposto pelo Telegram
MESSAGE_LIMIT = 4096


def split_message(text: str, limit: int = MESSAGE_LIMIT) -> list[str]:
    """Quebra o texto em partes de até limit caracteres, sem cortar linhas."""
    chunks: list[str] = []
    current = ""
    for line in text.split("\n"):
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > limit and current:
            chunks.append(current)
            current = line
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks
