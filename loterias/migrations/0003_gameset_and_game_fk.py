import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("loterias", "0002_add_prize_tiers_to_contest"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="GameSet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="game_sets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Game Set",
                "verbose_name_plural": "Game Sets",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="gameset",
            constraint=models.UniqueConstraint(
                fields=("user", "name"),
                name="unique_gameset_name_per_user",
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="game_set",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="games",
                to="loterias.gameset",
            ),
        ),
    ]
