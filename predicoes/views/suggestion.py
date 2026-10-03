from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from predicoes.services import GenerateSuggestionsService

_MIN_COUNT = 1
_MAX_COUNT = 10
_MIN_SIZE = 15
_MAX_SIZE = 20


class SuggestionView(APIView):
    """Gera sugestões de jogos a partir da frequência dos últimos concursos."""

    def post(self, request: Request) -> Response:
        try:
            count = int(request.data.get("count", 1))
            size = int(request.data.get("size", 15))
        except (TypeError, ValueError):
            return Response({"detail": "Informe números válidos."}, status=status.HTTP_400_BAD_REQUEST)
        if count < _MIN_COUNT or count > _MAX_COUNT or size < _MIN_SIZE or size > _MAX_SIZE:
            return Response(
                {"detail": "Escolha de 1 a 10 jogos, com 15 a 20 dezenas."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        games = GenerateSuggestionsService().generate(count=count, size=size)
        return Response({"games": games, "count": count, "size": size})
