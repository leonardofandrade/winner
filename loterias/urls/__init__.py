from django.urls import include, path

urlpatterns = [
    path("contests/", include("loterias.urls.contest_urls")),
    path("games/", include("loterias.urls.game_urls")),
    path("game-sets/", include("loterias.urls.game_set_urls")),
]
