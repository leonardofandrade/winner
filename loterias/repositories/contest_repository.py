from loterias.models import Contest
from loterias.parsers import ParsedContest


class ContestRepository:
    """Encapsula todo acesso ORM ao model Contest."""

    def get_by_number(self, number: int) -> Contest | None:
        return Contest.objects.filter(number=number).first()

    def get_latest_number(self) -> int | None:
        # Retorna o número do concurso mais recente no banco, ou None se vazio
        contest = Contest.objects.order_by("-number").first()
        return contest.number if contest else None

    def update_or_create(self, data: ParsedContest) -> tuple[Contest, bool]:
        """Cria ou atualiza um concurso. Retorna (contest, created)."""
        defaults = {k: v for k, v in data.items() if k != "number"}
        return Contest.objects.update_or_create(number=data["number"], defaults=defaults)
