import asyncio

from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from loterias.models import Contest
from loterias.repositories import ContestRepository, GameResultRepository
from loterias.serializers import ContestSerializer, GameResultSerializer
from loterias.services import ImportLotofacilService

_contest_repo = ContestRepository()
_result_repo = GameResultRepository()


class ContestListView(generics.ListAPIView):
    serializer_class = ContestSerializer

    def get_queryset(self):
        return Contest.objects.order_by("-number")


class ContestDetailView(generics.RetrieveAPIView):
    serializer_class = ContestSerializer
    lookup_field = "number"

    def get_queryset(self):
        return Contest.objects.all()


class ContestImportView(APIView):
    """Importa um concurso específico ou o mais recente da API da Caixa."""

    def post(self, request: Request) -> Response:
        number = request.data.get("number")
        service = ImportLotofacilService()
        contest = asyncio.run(service.import_contest(number))
        return Response(ContestSerializer(contest).data, status=status.HTTP_200_OK)


class ContestResultsView(generics.ListAPIView):
    serializer_class = GameResultSerializer

    def get_queryset(self):
        contest = generics.get_object_or_404(Contest, number=self.kwargs["number"])
        return _result_repo.get_for_contest(contest)
