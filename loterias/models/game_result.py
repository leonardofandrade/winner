from django.db import models

from .contest import Contest
from .game import Game


class GameResult(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="results")
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="game_results")
    # Quantidade de acertos do jogo neste concurso
    hits = models.PositiveSmallIntegerField()
    # Prêmio recebido (0 se não premiado)
    prize = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("game", "contest")]
        ordering = ["-created_at"]
        verbose_name = "Game Result"
        verbose_name_plural = "Game Results"

    def __str__(self) -> str:
        return f"Result: Game #{self.game_id} × Contest #{self.contest.number} — {self.hits} hits"
