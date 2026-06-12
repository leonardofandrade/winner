from django.urls import path

from loterias.views.game_views import (
    GameCalculateView,
    GameDetailView,
    GameListCreateView,
    GameResultsView,
)

urlpatterns = [
    path("", GameListCreateView.as_view(), name="game-list"),
    path("<int:pk>/", GameDetailView.as_view(), name="game-detail"),
    path("<int:pk>/calculate/", GameCalculateView.as_view(), name="game-calculate"),
    path("<int:pk>/results/", GameResultsView.as_view(), name="game-results"),
]
