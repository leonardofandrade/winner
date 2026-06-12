import asyncio
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from loterias.services import ImportLotofacilService


class Command(BaseCommand):
    help = "Import Lotofacil contests from Caixa API or XLSX file"

    def add_arguments(self, parser) -> None:
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument("--number", type=int, help="Import a specific contest number")
        mode.add_argument("--latest", action="store_true", help="Import the latest contest")
        mode.add_argument("--sync", action="store_true", help="Import only missing contests since last DB entry")
        mode.add_argument("--xls", action="store_true", help="Download full history XLSX from Caixa")
        mode.add_argument("--xls-file", type=str, dest="xls_file", help="Import from local XLSX file")
        parser.add_argument("--from", type=int, dest="from_number", help="Start of range (use with --to)")
        parser.add_argument("--to", type=int, dest="to_number", help="End of range (use with --from)")

    def handle(self, *args, **options) -> None:
        service = ImportLotofacilService()

        if options["sync"]:
            latest, imported = asyncio.run(service.sync())
            if imported == 0:
                self.stdout.write(f"Already up to date at contest #{latest}.")
            else:
                self.stdout.write(self.style.SUCCESS(f"Sync complete: {imported} contests imported (up to #{latest})."))

        elif options["xls_file"]:
            path = Path(options["xls_file"])
            if not path.exists():
                raise CommandError(f"File not found: {path}")
            xls_bytes = path.read_bytes()
            total = asyncio.run(service.import_all_from_xls(xls_bytes))
            self.stdout.write(self.style.SUCCESS(f"Imported {total} contests from {path.name}."))

        elif options["xls"]:
            self.stdout.write("Downloading XLSX from Caixa...")
            xls_bytes = asyncio.run(service._client.fetch_xls())
            total = asyncio.run(service.import_all_from_xls(xls_bytes))
            self.stdout.write(self.style.SUCCESS(f"Imported {total} contests."))

        elif options["from_number"] and options["to_number"]:
            contests = asyncio.run(
                service.import_range(options["from_number"], options["to_number"])
            )
            self.stdout.write(self.style.SUCCESS(f"Imported {len(contests)} contests."))

        else:
            number = options.get("number")
            contest = asyncio.run(service.import_contest(number))
            self.stdout.write(self.style.SUCCESS(f"Contest #{contest.number} imported."))
