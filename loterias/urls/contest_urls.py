from django.urls import path

from loterias.views.contest_views import (
    ContestDetailView,
    ContestImportView,
    ContestListView,
    ContestResultsView,
)

urlpatterns = [
    path("", ContestListView.as_view(), name="contest-list"),
    path("import/", ContestImportView.as_view(), name="contest-import"),
    path("<int:number>/", ContestDetailView.as_view(), name="contest-detail"),
    path("<int:number>/results/", ContestResultsView.as_view(), name="contest-results"),
]
