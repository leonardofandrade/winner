class WinnerException(Exception):
    """Exceção base do projeto Winner."""


class ClientError(WinnerException):
    """Erro ao comunicar com API externa."""


class ParseError(WinnerException):
    """Erro ao converter dados brutos em estrutura Python."""
