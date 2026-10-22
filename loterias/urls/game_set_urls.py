from django.urls import path

from loterias.views.game_views import GameSetDetailView

urlpatterns = [
    path("<int:pk>/", GameSetDetailView.as_view(), name="game-set-detail"),
]
