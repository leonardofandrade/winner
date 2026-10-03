from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


def _user_payload(user) -> dict:
    return {"id": user.pk, "username": user.username}


@method_decorator(ensure_csrf_cookie, name="dispatch")
class FrontendView(TemplateView):
    template_name = "frontend/index.html"


class LoginView(APIView):
    def post(self, request: Request) -> Response:
        username = str(request.data.get("username", "")).strip()
        password = str(request.data.get("password", ""))
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "Usuário ou senha incorretos."}, status=status.HTTP_401_UNAUTHORIZED)
        login(request, user)
        return Response(_user_payload(user))


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(_user_payload(request.user))
