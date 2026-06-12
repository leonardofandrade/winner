from django.contrib import admin

from loterias.models import Contest, Game, GameResult


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ["number", "draw_date", "accumulated", "created_at"]
    search_fields = ["number"]
    list_filter = ["accumulated"]
    ordering = ["-number"]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at"]
    search_fields = ["user__username"]
    ordering = ["-created_at"]


@admin.register(GameResult)
class GameResultAdmin(admin.ModelAdmin):
    list_display = ["id", "game", "contest", "hits", "prize", "created_at"]
    list_filter = ["hits"]
    ordering = ["-created_at"]
