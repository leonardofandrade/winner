from django.conf import settings
from django.db import models


class Game(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="games",
    )
    # Lista de 15 a 20 números escolhidos pelo usuário (1-25)
    numbers = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Game"
        verbose_name_plural = "Games"

    def __str__(self) -> str:
        return f"Game #{self.pk} — user {self.user_id}"
