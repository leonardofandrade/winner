from django.db import models


class Contest(models.Model):
    # Número oficial do concurso da Lotofácil
    number = models.PositiveIntegerField(unique=True)
    draw_date = models.DateField()
    # Lista com os 15 números sorteados (1-25)
    winning_numbers = models.JSONField()
    # Valor total arrecadado no concurso
    prize_pool = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    accumulated = models.BooleanField(default=False)
    # Rateio por faixa: {"15": "22711.50", "14": "1234.00", ...} — None quando não disponível
    prize_tiers = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-number"]
        verbose_name = "Contest"
        verbose_name_plural = "Contests"

    def __str__(self) -> str:
        return f"Contest #{self.number} — {self.draw_date}"
