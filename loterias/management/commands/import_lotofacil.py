import asyncio

from django.core.management.base import BaseCommand

from loterias.services import ImportLotofacilService


class Command(BaseCommand):
    help = "Import Lotofacil contests from Caixa API"

    def add_arguments(self, parser) -> None:
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--number", type=int, help="Import a specific contest number")
        group.add_argument("--latest", action="store_true", help="Import the latest contest")
        parser.add_argument("--from", type=int, dest="from_number", help="Start of range")
        parser.add_argument("--to", type=int, dest="to_number", help="End of range")

    def handle(self, *args, **options) -> None:
        service = ImportLotofacilService()

        if options["from_number"] and options["to_number"]:
            contests = asyncio.run(
                service.import_range(options["from_number"], options["to_number"])
            )
            self.stdout.write(self.style.SUCCESS(f"Imported {len(contests)} contests."))
        else:
            number = options.get("number")
            contest = asyncio.run(service.import_contest(number))
            self.stdout.write(self.style.SUCCESS(f"Contest #{contest.number} imported."))
