from django.core.management.base import BaseCommand, CommandError

from loterias.repositories import ContestRepository, GameRepository
from loterias.services import ResultCalculationService


class Command(BaseCommand):
    help = "Calculate game results against Lotofacil contests"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--contest", type=int, dest="contest_number", help="Contest number to calculate")
        parser.add_argument("--game", type=int, dest="game_id", help="Game ID to calculate")

    def handle(self, *args, **options) -> None:
        service = ResultCalculationService()
        contest_number = options.get("contest_number")
        game_id = options.get("game_id")

        if contest_number and game_id:
            # Calcula um jogo específico contra um concurso específico
            contest = ContestRepository().get_by_number(contest_number)
            if not contest:
                raise CommandError(f"Contest #{contest_number} not found.")
            game = GameRepository().get_by_id(game_id)
            if not game:
                raise CommandError(f"Game #{game_id} not found.")
            result = service.calculate(game, contest)
            self.stdout.write(self.style.SUCCESS(
                f"Game #{game_id} vs Contest #{contest_number}: {result.hits} hits, R${result.prize}"
            ))

        elif contest_number:
            contest = ContestRepository().get_by_number(contest_number)
            if not contest:
                raise CommandError(f"Contest #{contest_number} not found.")
            results = service.calculate_all_for_contest(contest)
            self.stdout.write(self.style.SUCCESS(f"{len(results)} results calculated for Contest #{contest_number}."))

        elif game_id:
            game = GameRepository().get_by_id(game_id)
            if not game:
                raise CommandError(f"Game #{game_id} not found.")
            results = service.calculate_all_for_game(game)
            self.stdout.write(self.style.SUCCESS(f"{len(results)} results calculated for Game #{game_id}."))

        else:
            raise CommandError("Provide --contest, --game, or both.")
