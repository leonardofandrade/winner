from django.urls import path

from predicoes.views.suggestion import SuggestionView

urlpatterns = [
    path("", SuggestionView.as_view(), name="suggestion-create"),
]
