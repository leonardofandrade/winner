from django.conf import settings
from django.db import models


class GameSet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="game_sets",
    )
    # Apelido escolhido pelo usuário para o conjunto
    name = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Game Set"
        verbose_name_plural = "Game Sets"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_gameset_name_per_user",
            ),
        ]

    def __str__(self) -> str:
        return self.name
