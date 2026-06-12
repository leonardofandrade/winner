from loterias.models import Contest
from loterias.parsers import ParsedContest


class ContestRepository:
    """Encapsula todo acesso ORM ao model Contest."""

    def get_by_number(self, number: int) -> Contest | None:
        return Contest.objects.filter(number=number).first()

    def get_latest(self) -> Contest | None:
        return Contest.objects.order_by("-number").first()

    def get_recent(self, n: int) -> list[Contest]:
        """Retorna os n concursos mais recentes ordenados do mais antigo ao mais novo."""
        return list(Contest.objects.order_by("-number")[:n])

    def get_latest_number(self) -> int | None:
        # Retorna o número do concurso mais recente no banco, ou None se vazio
        contest = Contest.objects.order_by("-number").first()
        return contest.number if contest else None

    def update_or_create(self, data: ParsedContest) -> tuple[Contest, bool]:
        """Cria ou atualiza um concurso. Retorna (contest, created)."""
        defaults = {k: v for k, v in data.items() if k != "number"}
        return Contest.objects.update_or_create(number=data["number"], defaults=defaults)

    def bulk_update_or_create(self, items: list[ParsedContest]) -> int:
        """Insere ou atualiza em lote. Retorna o total processado."""
        objects = [
            Contest(
                number=d["number"],
                draw_date=d["draw_date"],
                winning_numbers=d["winning_numbers"],
                prize_pool=d["prize_pool"],
                accumulated=d["accumulated"],
                prize_tiers=d.get("prize_tiers"),
            )
            for d in items
        ]
        Contest.objects.bulk_create(
            objects,
            update_conflicts=True,
            unique_fields=["number"],
            update_fields=["draw_date", "winning_numbers", "prize_pool", "accumulated", "prize_tiers"],
        )
        return len(objects)
