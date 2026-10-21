from django.db import connection

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

    def drawn_combinations(self) -> set[tuple[int, ...]]:
        """Combinações de 15 dezenas que já saíram em algum concurso."""
        return {
            tuple(sorted(numbers))
            for numbers in Contest.objects.values_list("winning_numbers", flat=True)
        }

    def get_latest_number(self) -> int | None:
        # Retorna o número do concurso mais recente no banco, ou None se vazio
        contest = Contest.objects.order_by("-number").first()
        return contest.number if contest else None

    def get_after(self, number: int, limit: int) -> list[Contest]:
        """Até limit concursos posteriores a number, os mais recentes, do mais antigo ao mais novo."""
        recent = Contest.objects.filter(number__gt=number).order_by("-number")[:limit]
        return sorted(recent, key=lambda c: c.number)

    def get_missing_numbers(self, up_to: int) -> list[int]:
        """Números ausentes entre o menor concurso do banco e up_to (inclusive)."""
        earliest = Contest.objects.order_by("number").values_list("number", flat=True).first()
        if earliest is None:
            return []
        existing = set(Contest.objects.filter(number__gte=earliest).values_list("number", flat=True))
        return [n for n in range(earliest, up_to + 1) if n not in existing]

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
        # MySQL faz o upsert por qualquer chave única e rejeita unique_fields.
        # SQLite e PostgreSQL exigem unique_fields para saber qual conflito atualizar.
        upsert = {
            "update_conflicts": True,
            "update_fields": [
                "draw_date",
                "winning_numbers",
                "prize_pool",
                "accumulated",
                "prize_tiers",
            ],
        }
        if connection.features.supports_update_conflicts_with_target:
            upsert["unique_fields"] = ["number"]
        Contest.objects.bulk_create(objects, **upsert)
        return len(objects)
