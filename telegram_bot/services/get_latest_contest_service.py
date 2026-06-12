from loterias.models import Contest
from loterias.repositories import ContestRepository


class GetLatestContestService:
    """Retorna o concurso mais recente cadastrado no banco."""

    def __init__(self) -> None:
        self._repo = ContestRepository()

    def execute(self) -> Contest | None:
        return self._repo.get_latest()
