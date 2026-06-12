from django.urls import include, path

urlpatterns = [
    path("contests/", include("loterias.urls.contest_urls")),
    path("games/", include("loterias.urls.game_urls")),
]
