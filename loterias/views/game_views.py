from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from loterias.repositories import GameRepository, GameResultRepository
from loterias.serializers import GameResultSerializer, GameSerializer
from loterias.services import ResultCalculationService

_game_repo = GameRepository()
_result_repo = GameResultRepository()


class GameListCreateView(generics.ListCreateAPIView):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _game_repo.get_by_user(self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)


class GameDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _game_repo.get_by_user(self.request.user)


class GameCalculateView(APIView):
    """Calcula resultados de um jogo contra todos os concursos cadastrados."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk: int) -> Response:
        game = generics.get_object_or_404(
            _game_repo.get_by_user(request.user), pk=pk
        )
        results = ResultCalculationService().calculate_all_for_game(game)
        return Response({"calculated": len(results)}, status=status.HTTP_200_OK)


class GameResultsView(generics.ListAPIView):
    serializer_class = GameResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        game = generics.get_object_or_404(
            _game_repo.get_by_user(self.request.user), pk=self.kwargs["pk"]
        )
        return _result_repo.get_for_game(game)
